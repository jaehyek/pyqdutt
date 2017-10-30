# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
#date:
#---------------------------------------------------------
import subprocess
import argparse
from datetime import datetime
import pprint
import time

""" 다음은 QDUTT의 command 와 Option이다. 
-case=ownaddressrwtest --sdraminterface=0 --sdramchipselect=0
-case=addresslinestest --sdraminterface=0 --sdramchipselect=0
-case=datalinestest --sdraminterface=0 --sdramchipselect=0
-case=readtest --sdraminterface=0 --sdramchipselect=0 --loopcount=1 --infinityflag=0 --pattern=-1
-case=writetest --sdraminterface=0 --sdramchipselect=0 --loopcount=1 --infinityflag=0 --pattern=-1
-case=readwritetest --sdraminterface=0 --sdramchipselect=0 --loopcount=1 --infinityflag=0 --pattern=-1
-case=retrain
-case=changebimcphysettings --testline=0 --prfslevel=0 --overdrive=0 --pullup=0 --odt=0 --voh=0 --en_term=0
-case=readpowersetting
-case=readphysetting --testline=0 --prfslevel=0
-case=readtemperature
-case=changebimcclock --clockvalue=6
-case=changevddq --vddqvalue=1060
-case=changevdd1 --vdd1value=0
-case=disabledbi
-case=changemr3 --freq=6 --mr3val=-1
-case=changemr11 --freq=6 --mr11val=-1
-case=mrwrite --sdraminterface=0 --sdramchipselect=0 --regnum=5 --regvalue=-1

clkplan: 
0 - 100000,
1 - 150000,
2 - 200000,
3 - 300000,
4 - 412800,
5 - 547200,
6 - 681600,
7 - 768000,
8 - 1017600,
9 - 1296000,
10 - 1555200,
11 - 1804800,
"""

ownaddressrwtest = "-case=ownaddressrwtest --sdraminterface=%s --sdramchipselect=%s"
addresslinestest = "-case=addresslinestest --sdraminterface=%s --sdramchipselect=%s"
datalinestest = "-case=datalinestest --sdraminterface=%s --sdramchi pselect=%s"
readtest = "-case=readtest --sdraminterface=%s --sdramchipselect=%s --loopcount=%s --infinityflag=%s --pattern=%s"
writetest = "-case=writetest --sdraminterface=%s --sdramchipselect=%s --loopcount=%s --infinityflag=%s --pattern=%s"
readwritetest = "-case=readwritetest --sdraminterface=%s --sdramchipselect=%s --loopcount=%s --infinityflag=%s --pattern=%s"
retrain = "-case=retrain"
changebimcphysettings = "-case=changebimcphysettings --testline=%s --prfslevel=%s --overdrive=%s --pullup=%s --odt=%s --voh=%s --en_term=%s"
readpowersetting = "-case=readpowersetting"
readphysetting = "-case=readphysetting --testline=%s --prfslevel=%s"
readtemperature = "-case=readtemperature"
changebimcclock = "-case=changebimcclock --clockvalue=%s"
changevddq = "-case=changevddq --vddqvalue=%s"
changevdd1 = "-case=changevdd1 --vdd1value=%s"
disabledbi = "-case=disabledbi"
changemr3 = "-case=changemr3 --freq=%s --mr3val=%s"
changemr11 = "-case=changemr11 --freq=%s --mr11val=%s"
mrwrite = "-case=mrwrite --sdraminterface=%s --sdramchipselect=%s --regnum=%s --regvalue=%s"




global comport, comload, cmd, hlog

cmd = "QDUTTCommand.exe "
cmdinit = cmd + "-init"
cmdexit = cmd + "-exit"
cmdhello = cmd + "-hello"
ddiname = "C:\\QUALCOMM\\QDUTT\\mbn\\8996\\DDRDebugImage_8996_sec_signning.elf"
cmdload = ""
comport = ""
hlog = 0

def make_bytesmsg_to_liststr(bytesmsg) :
    try:
        listretmsg = bytesmsg.strip().decode("utf-8").split("\r\n")
        # pprint.pprint(listretmsg)
        return listretmsg[-2]
    except:
        return "UnicodeDecodeError: 'utf-8' codec can't decode byte"


def print_proc_output(listlines):
    for line in listlines :
        print(line.strip())

listok = ["ok", "pass", "done"]
def check_pass_ok(strmsg) :
    global hlog
    listresult = [ aa in strmsg.lower() for aa in listok ]

    ret =  any(listresult)
    strret = "%s" % ret

    if "UnicodeDecodeError" in strmsg :
        strret = "UnicodeDecodeError"
        ret = "UnicodeDecodeError"
    elif "Device already loaded" in strmsg :
        ret = True
        strret = "%s" % ret

    print(strret)
    hlog.write(strret + "\n")

    # print out the strmsg
    strtemp = "--> " + strmsg
    print(strtemp)
    hlog.write(strtemp + "\n")

    return ret

def cmd_execute(cmdstr):
    global hlog
    msg = "%s : Execute : "%(datetime.now()) + cmdstr + " : "
    print(msg, end="")
    hlog.write(msg)
    p = subprocess.Popen(cmdstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = p.communicate()
    return output

def qdutt_init(clsvar):
    global cmd, cmdload, ddiname, comport, cmdinit, cmdhello
    # make load command
    cmdload = "%s -load --port=%s --file=%s"%(cmd, comport,ddiname )

    listcmd = [cmdinit, cmdhello, cmdload]
    for cmdtemp in listcmd:
        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdtemp))) == False:
            print("..... fail .....")
            return False


def qdutt(clsvar):
    """
    GDUTT 전체 수행 함수
    :param clsvar: parameter 전달.
    :return: 
    """
    global  cmd, comport

    # 초기화하기
    if qdutt_init(clsvar) == False:
        return

    # retain command
    cmdretain = "%s -run --port=%s --case=retrain"%(cmd, comport)
    cmdclock = "%s -run --port=%s --case=changebimcclock --clockvalue=%s"
    cmdvddq = "%s -run --port=%s --case=changevddq --vddqvalue=%s"
    cmdvdd1 = "%s -run --port=%s --case=changevdd1 --vdd1value=%s"

    cmdownaddress = "%s -run --port=%s --case=ownaddressrwtest --sdraminterface=%s --sdramchipselect=%s"
    cmdaddressline = "%s -run --port=%s --case=addresslinestest --sdraminterface=%s --sdramchipselect=%s"
    cmddataline = "%s -run --port=%s --case=datalinestest --sdraminterface=%s --sdramchipselect=%s"

    # define the loop condition
    listsdraminterface = [0,1]
    listsdramchipselect = [0,1]
    listclockplan = [aa for aa in range(7,12)]
    # listclockplan = [aa for aa in range(9, 12)]
    listVDDQ = [1060,1125, 1160 ]
    listVDD1 = [1700, 1800, 1900]

    # do retain command
    if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdretain))) == False:
        print("..... fail .....")
        return False
    else:
        # reload the elf image
        time.sleep(20)
        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdload))) == False:
            print("..... fail .....")
            return False
        time.sleep(5)

    for clockplan in listclockplan :
        # change clock
        cmdclocktemp = cmdclock%(cmd, comport, clockplan)
        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdclocktemp))) == False:
            print("..... fail .....")
            return False

        for vddq in listVDDQ :
            for vdd1 in listVDD1 :
                cmdvddqtemp = cmdvddq%(cmd,comport, vddq)
                cmdvdd1temp = cmdvdd1%(cmd,comport, vdd1)
                check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdvddqtemp)))
                check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdvdd1temp)))

                for sdraminterface in listsdraminterface :
                    for sdramchipselect in listsdramchipselect :
                        cmdownaddresstemp = cmdownaddress%(cmd, comport,sdraminterface, sdramchipselect )
                        cmdaddresslinetemp = cmdaddressline%(cmd, comport, sdraminterface, sdramchipselect)
                        cmddatalinetemp = cmddataline%(cmd, comport, sdraminterface, sdramchipselect)

                        strloopstatus = ">>> condition : clock=%s, vddq=%s, vdd1=%s, interface=%s, chipselect=%s \n" % (
                                clockplan,vddq,vdd1,sdraminterface,sdramchipselect  )
                        hlog.write(strloopstatus)
                        print(strloopstatus)


                        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdownaddresstemp))) == False:
                            strfailcondition = "@@@ fail : clock=%s, vddq=%s, vdd1=%s, interface=%s, chipselect=%s, case=ownaddresstest\n" % (
                                clockplan,vddq,vdd1,sdraminterface,sdramchipselect  )
                            hlog.write(strfailcondition)
                            print(strfailcondition)

                        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmdaddresslinetemp))) == False:
                            strfailcondition = "@@@ fail : clock=%s, vddq=%s, vdd1=%s, interface=%s, chipselect=%s, case=addresslinetest\n" % (
                                clockplan, vddq, vdd1, sdraminterface, sdramchipselect)
                            hlog.write(strfailcondition)
                            print(strfailcondition)
                        if check_pass_ok(make_bytesmsg_to_liststr(cmd_execute(cmddatalinetemp))) == False:
                            strfailcondition = "@@@ fail : clock=%s, vddq=%s, vdd1=%s, interface=%s, chipselect=%s, case=datalinetest\n" % (
                                clockplan, vddq, vdd1, sdraminterface, sdramchipselect)
                            hlog.write(strfailcondition)
                            print(strfailcondition)


if __name__ == "__main__" :
    cmdlineopt = argparse.ArgumentParser(description='Execute the QDUTTCommand and get the log  ')
    cmdlineopt.add_argument('-port', action="store", dest="port", default='COM11', help='COM port number')
    cmdlineopt.add_argument('-log', action="store", dest="logname", default='logname.txt', help='log file name')
    clsvar = cmdlineopt.parse_args()

    if  clsvar.port[0:3] == "COM" and type(int(clsvar.port[3:])) == int :
        comport = clsvar.port
    else:
        print("please set the COM port properly")

    # check the log extenstion as txt.
    if clsvar.logname[-4:].lower() != ".txt" :
        print("please enter the log extenstion as txt type")
        exit(0)
    clsvar.logname = clsvar.port + "_" +  clsvar.logname
    hlog = open(clsvar.logname, "a")

    timestart = datetime.now()
    qdutt(clsvar)
    timeend = datetime.now()
    msgend = " elasped time is : %s "%(timeend - timestart)
    hlog.write(msgend)
    print(msgend)

    cmd_execute(cmdexit)
    hlog.close()







