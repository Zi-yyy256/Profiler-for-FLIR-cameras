# Profiler-for-FLIR-cameras
This profiler can give real-time gaussian fit of optical spots.

Chinese version:
使用方法：
1. 在本地安装相机驱动,运行文件夹中的SpinnakerSDK_FULL_4.0.0.116_x64.exe。
2. 连接相机，进入profiler文件夹：后缀PID指PID方法调整曝光，noPID指可以手动调整曝光。每个profiler文件夹中有相应的py文件。再进入dist文件夹，找到相应的exe文件，双击即可运行。

若相机运行不正常，请检查驱动安装、USB接口（有问题的USB接口会让相机获取的图像产生条纹）。若是.exe文件的问题，请用cmd运行相应.exe文件，即可查看报错。

——————————————————————————————————————————————————————————————————————————————

查看报错方式：直接在命令行cmd运行exe文件，可以查看报错信息。

测试相机型号：Teledyne FLIR CM3-U3-50S5M-CS USB3 Mono Camera
适用型号：Teledyne FLIR任意相机（与SpinnakerSDK兼容）

驱动：spinnaker SDK 4.0.0.116 for windows，可以在官网上找到，下载Spinnaker Full SDK 4.0.0.116 (64-bit Full installer)。在Spinnaker安装步骤中，选择两个USB driver即可（不同相机不同选择）。（保持怀疑态度，有可能需要全部安装，最好默认的都装上。Gige driver不用）

pyinstaller版本6.7.0
numpy版本1.26.4

——————————————————————————————————————————————————————————————————————————————

关于代码（.py文件的运行）：

查看报错方式：直接在命令行cmd运行.exe文件，可以查看报错信息。

报错1：
OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. That is dangerous, since it can degrade performance or cause incorrect results. The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results. For more information, please see http://www.intel.com/software/products/support/.
解决方案:
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

报错2：
运行pyinstaller生成的exe时有提示
INTEL MKL ERROR: The specified module could not be found. mkl_intel_thread.2.dll.
Intel MKL FATAL ERROR: Cannot load mkl_intel_thread.2.dll.
解决方案：
将运行py文件的虚拟环境中（或没有虚拟环境就在base下），进入Library\bin文件夹，复制其中所有的mkl文件，粘贴到生成的exe所属文件夹下，即可正常运行。（如果没有，就先在该环境下pip install mkl和pip install mkl-service）


English version:
Usage Instructions:

Install the camera driver locally and run SpinnakerSDK_FULL_4.0.0.116_x64.exe from the folder.
Connect the camera and navigate to the profiler folder:
Files with the suffix PID use the PID method to adjust exposure.
Files with the suffix noPID allow manual exposure adjustment.
Each profiler folder contains corresponding .py files. Then, go to the dist folder, find the corresponding .exe file, and double-click it to run.
If the camera does not work properly, check the following:

Ensure the driver is correctly installed.
Verify the USB port (a faulty USB port may cause striped images from the camera).
If the issue is related to the .exe file, run it via cmd to view the error messages.
How to Check Error Messages:
Run the .exe file directly in the command prompt (cmd) to view error details.

Tested Camera Model:
Teledyne FLIR CM3-U3-50S5M-CS USB3 Mono Camera

Compatible Models:
Any Teledyne FLIR camera compatible with SpinnakerSDK

Driver:
Spinnaker SDK 4.0.0.116 for Windows. It can be downloaded from the official website. Download the Spinnaker Full SDK 4.0.0.116 (64-bit Full installer). During installation, select both USB drivers (options may vary for different cameras).
(Tip: It's recommended to install all available components for better compatibility. Gige driver is not required.)

Software Versions:

pyinstaller version: 6.7.0
numpy version: 1.26.4
About the Code (Running .py Files):

How to Check Error Messages:
Run the .exe file directly in the command prompt (cmd) to view error details.

Error 1:
OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.  
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. That is dangerous, since it can degrade performance or cause incorrect results. The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results. For more information, please see http://www.intel.com/software/products/support/.

Solution:
Add the following code to the script:
import os  
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
