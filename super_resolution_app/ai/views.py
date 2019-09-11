from django.shortcuts import render, redirect
import os
from django.views.decorators.http import require_http_methods
import base64
import random
from time import sleep
import time
import sys, os
from torchvision.datasets.utils import download_and_extract_archive
from mypy.checkexpr import Finished
from scp import SCPException


# Create your views here.
def index(request):
    return render(request, 'ai/index.html')

def top(request):
    return render(request, 'ai/top.html')

def resolution(request):
    return render(request, "ai/resolution.html")

def resolution_example(request):
    return render(request, 'ai/resolution_example.html')

def doResolution(request):

    #conect server with ssh
    import paramiko
    import scp

    #define form
    from .form import UploadFileForm

    #update file save directory
#     UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'  # アップロードしたファイルを保存するディレクトリ
    UPLOAD_DIR = "C:\\Users\\sd18064\\Desktop\\labolatory\\super_resolution_app\\super_resolution_app\\super_resolution_app\\static\\uploads\\"
#     DOWNLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/downloads/' #ダウンロードしたファイルを保存するディレクトリ
    DOWNLOAD_DIR = "C:\\Users\\sd18064\\Desktop\\labolatory\\super_resolution_app\\super_resolution_app\\super_resolution_app\\static\\downloads\\"

    EXPANSION_DIR = "C:\\Users\\sd18064\\Desktop\\labolatory\\super_resolution_app\\super_resolution_app\\super_resolution_app\\static\\expansions\\"

    #画像データの取得
    file = request.FILES.getlist("file")

#     ファイルが選択されていない場合
    if len(file) == 0:
        context = {
            "message": "ファイルをアップロードしてください。"
           }
        return render(request, "ai/resolution.html", context)

#     ファイルが複数選択されていた場合
    elif len(file) != 1:
        context = {
            "message": "ファイルは1つのみアップロードしてください。"
           }
        return render(request, "ai/resolution.html", context)

    # アップロードされたファイルのハンドル
    def handle_uploaded_file(f, file_name):
        path = os.path.join(UPLOAD_DIR, file_name)
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    # 拡大されたファイルのハンドル
    def handle_expansion_file(f, file_name):
        path = os.path.join(EXPANSION_DIR, file_name)
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

#             make random file name
            root, ext = os.path.splitext(file[0].name)
            file_name = str(random.random()) + ext

#             delete exist files name
            DOWNLOAD_FILES_DIR = DOWNLOAD_DIR
            download_files_list = os.listdir(DOWNLOAD_FILES_DIR)

            UPLOAD_FILES_DIR = UPLOAD_DIR
            upload_files_list = os.listdir(UPLOAD_FILES_DIR)

            EXPANSION_FILES_DIR = EXPANSION_DIR
            expansion_files_list = os.listdir(EXPANSION_FILES_DIR)

#             delete file part
            for download_file in download_files_list:
                if download_file == file_name or download_file == "result_files.txt":
                    pass
                else:
                    os.remove(os.path.join(DOWNLOAD_FILES_DIR, download_file))

            for upload_file in upload_files_list:
                if upload_file == file_name:
                    pass
                else:
                    os.remove(os.path.join(UPLOAD_FILES_DIR, upload_file))

            for expansion_file in expansion_files_list:
                if expansion_file == file_name:
                    pass
                else:
                    os.remove(os.path.join(EXPANSION_FILES_DIR, expansion_file))
#             upload local server
            handle_uploaded_file(request.FILES['file'], file_name)

#                 delete file_name file
            DELETE_INPUTS_DIR =  "cd DBPN-Pytorch/Input/nakatani_data"
            DELETE_INPUTS_COMMAND = "rm " + file_name
            DELETE_RESULTS_DIR = "cd DBPN-Pytorch/Results/nakatani_data"
            DELETE_RESULTS_COMMAND = "rm " + file_name

            magnification = request.POST.get("magnification_rate" ,None)

#             connect remote server
            with paramiko.SSHClient() as ssh:
#                 auth method
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname='133.21.219.152', port=22, username='nakatani', password='54ea8gra86ahra')

                #create scp object
                scp_client_1 = scp.SCPClient(ssh.get_transport())

                #upload one file to remote directry
                scp_client_1.put(UPLOAD_DIR + file_name, recursive=True, remote_path="/home/nakatani/DBPN-Pytorch/Input/nakatani_data")
                scp_client_1.close()

#                 enter vertual_env
                enter_ver_env = "source DBPN-Pytorch/dbpn_env/bin/activate"
                move_dir = "cd DBPN-Pytorch/"

                #change magnification
                if magnification == "2":
                    eval_command = "python eval.py --model models/DBPN_x2.pth --upscale_factor 2"
                elif magnification == "4":
                    eval_command = "python eval.py --model models/DBPN_x4.pth --upscale_factor 4"
                elif magnification == "8":
                    eval_command = "python eval.py --model models/DBPN_x8.pth --upscale_factor 8"
                else:
                    eval_command = "python eval_gan.py"

                debag_command = " > debag.txt"
                exe_command = enter_ver_env + ";" + move_dir +";" + eval_command + debag_command
                stdin, stdout, stderr = ssh.exec_command(exe_command)

                finish_flag = True
                start_time = time.time()
                while(finish_flag):

                    #write files of Results dir
                    check_command = "python check_file.py"
                    stdin, stdout, stderr = ssh.exec_command(move_dir + ";" + check_command)

    #                     check success network worked
                    CHECK_PATH = os.path.join("/home/nakatani/DBPN-Pytorch/" , "result_files.txt")
                    scp_client_3 = scp.SCPClient(ssh.get_transport())

#                     for SCPException
                    try:
                        scp_client_3.get(CHECK_PATH, local_path=DOWNLOAD_DIR)

        #                 judgment success eval
                        with open(os.path.join(DOWNLOAD_DIR, "result_files.txt"), 'r') as check_file:
                            sentence = check_file.read()
                            if file_name in sentence:
                                finish_flag = False

    #                     check interval
                        sleep(3)
                        finish_time = time.time()

    #                     shut out long time session
                        if finish_time - start_time > 30:
                            stdin, stdout, stderr = ssh.exec_command(DELETE_INPUTS_DIR + ";" + DELETE_INPUTS_COMMAND)
                            scp_client_3.close()
                            context = {
                                "message": "接続が混雑しています。時間を置きもう一度お試しください"
                                }
                            return render(request, "ai/resolution.html", context)

                    except SCPException:
                        scp_client_3.close()
                        context = {
                            "message": "接続状況が悪いです。時間を置きもう一度お試しください"
                            }
                        return render(request, "ai/resolution.html", context)
                    scp_client_3.close()

                #download one file to local directry
                scp_client_2 = scp.SCPClient(ssh.get_transport())
                REMOTE_PATH = os.path.join("/home/nakatani/DBPN-Pytorch/Results/nakatani_data/" , file_name)
                scp_client_2.get(REMOTE_PATH, local_path=DOWNLOAD_DIR)



#                 delete file(Input or Result)
                stdin, stdout, stderr = ssh.exec_command(DELETE_INPUTS_DIR + ";" + DELETE_INPUTS_COMMAND)
                stdin, stdout, stderr = ssh.exec_command(DELETE_RESULTS_DIR + ";" + DELETE_RESULTS_COMMAND)

                scp_client_2.close()

#                 expansion_part
                import cv2
                img = cv2.imread(os.path.join(UPLOAD_DIR, file_name))
                img = cv2.resize(img, dsize=None, fx = int(magnification), fy = int(magnification), interpolation = 2 )
                cv2.imwrite(os.path.join(EXPANSION_DIR, file_name),img)

            context = {
            "file_name": file_name,
            "magnification_rate": magnification
           }
            return render(request, "ai/resolution_result.html", context)
    else:
        form = UploadFileForm()
        context = {
            "message": "アップロード失敗"
           }
        return render(request, "ai/resolution.html", context)


