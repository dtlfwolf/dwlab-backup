#!/usr/bin/env python3
#
import os
import pwd
import sys
from pathlib import Path
import subprocess

from dwlab-basicpy import dwlabRuntimeEnvironment
from dwlab-basicpy import dwlabSettings

import logging
from dwlab-basicpy import dwlabLogger
dwlabLogger.setup_logging()
logger=logging.getLogger(__name__)
__PACKAGE_NAME__ = "dwlab-backupclient"


class backupFile:
    def __init__(self, 
                 client=None,
                 package=None, 
                 job=None,
                 fileExtension=""
        ):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if isinstance(client,backupClient):
            self._backupClient=client
        else:
            logger.error("Given client is not of type backupClient")
            ValueError("Given client is not of type backupClient")
        if isinstance(package,backupPackage):
            self._backupPackage=package
        else:
            logger.error("Given package is not of type backupPackage")
            ValueError("Given package is not of type backupPackage")
        if isinstance(job,backupJob):
            self._backupJob=job
        else:
            logger.error("Given job is not of type backupJob")
            ValueError("Given job is not of type backupJob")
        if isinstance(fileExtension, str):
            self._fileExtension=fileExtension
        else:
            logger.error("File extension is not of type String")
            ValueError("File extension is not of type String")

        self._backupPath=Path.joinpath(
            Path.absolute(self._backupClient.backupMountPoint),
            self._backupPackage.backupPackageName
        )
        self.ensureBackupPath()
        self._backupFilename=str(self._backupJob.backupJobName)+"."+self._fileExtension

        logger.debug("Leaving function "+str(function_name))
    
    @property
    def backupFilename(self):
        return self._backupFilename 
    @property
    def backupPath(self):
        return self._backupPath
    @property
    def fileExtension(self):
        return self._fileExtension
    @property
    def filename(self):
        return Path.joinpath(
            self._backupPath,
            self._backupFilename
        )

    def ensureBackupPath(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))
        
        Path.mkdir(self._backupPath,parents=True,exist_ok=True)

        logger.debug("Leaving function "+str(function_name))
        return
    
class backupClient:
    def __init__(self, env=None, clientSettings=None, configFile=None, backupPackages=None):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        self._env=None
        self._clientSettings=None
        self._configFile=None
        self._backupPackages=[]

        if isinstance(env, dwlabRuntimeEnvironment):

            self._env=env
            if self._env._dwlab_package != "dwlab-backupclient":
                logger.info("The given environment is not a dwlab-backupclient environment.")
                logger.info("Switching to dwlab-backupclient environment.")
                

            settingsFile=Path.joinpath(self._env.dwlab_home,
                                       __PACKAGE_NAME__,
                                       "etc",
                                       "dwlabBackupClientSettings.yaml"
                                    )
            try:
                self._clientSettings=dwlabSettings.read_yaml(settingsFile)
            except Exception as e:
                logger.error("Cannot read installation setting.")
                raise(e)
            self._configFile=Path.joinpath(
                self._env.dwlab_home,
                __PACKAGE_NAME__,
                "etc",
                "dwlabBackupClientConfig.yaml"
            )
        if isinstance(clientSettings, dwlabSettings):
            if isinstance(env, dwlabRuntimeEnvironment):
                if self._clientSettings != clientSettings:
                    logger.error("Given client settings are not equal to the settings in the configuration file. Please check your code.")
                    raise ValueError("Given client settings are not equal to the settings in the configuration file. Please check your code.")
            else:
                self._clientSettings=clientSettings

        try:
            configuration=dwlabSettings.read_yaml(self._configFile)
            configSettings=configuration.data
            self._env=dwlabRuntimeEnvironment.from_dict(configSettings["env"])
            self._clientSettings=dwlabSettings(configSettings["clientSettings"])
            self._configFile=Path(configSettings["configFile"])
            backupPackagesDict=configSettings["backupPackages"]
            self._backupPackages=[]
            for backupPackageDict in backupPackagesDict:
                package=backupPackage.from_dict(backupPackageDict)
                self._backupPackages.append(package)

        except Exception as e:
            logger.warning("Cannot read configuration file.")
            logger.warning("Starting configuration with no backup packages.")
            
            configSettings=dict()
            configSettings["env"]=self._env.to_dict()
            configSettings["clientSettings"]=self._clientSettings.to_dict()
            configSettings["configFile"]=str(self._configFile)
            configSettings["backupPackages"]=[]

        logger.debug("Leaving function "+str(function_name))

    @property
    def backupMountPoint(self):
        return Path(self.clientSettings.get_variable("backupMountPoint"))

    @property
    def backupUser(self):
        return self.clientSettings.get_variable("backupUser")

    @property   
    def backupUserGroup(self):
        return self.clientSettings.get_variable("backupUserGroup")
    
    @property
    def backupUserGID(self):
        return self.clientSettings.get_variable("backupUserGID")

    @property
    def backupUserLoginAuthorizedKey(self):
        return self.clientSettings.get_variable("backupUserLoginAuthorizedKey")

    @property
    def backupMountType(self):
        return self.clientSettings.get_variable("backupMountType")

    @property
    def backupRemoteHost(self):
        return self.clientSettings.get_variable("backupRemoteHost")
    
    @property   
    def backupRemoteDir(self):
        return self.clientSettings.get_variable("backupRemoteDir")
    @property
    def backupFileServerUser(self):
        return self.clientSettings.get_variable("backupFileServerUser")
    @property
    def backupFileServerPassword(self):
        return self.clientSettings.get_variable("backupFileServerPassword")
    @property  
    def backupClientHostname(self):
        return self.clientSettings.get_variable("backupClientHostname")
    @property
    def backupLocation(self):
        return self.clientSettings.get_variable("backupLocation")
    @property
    def backupPackages(self):
        return self._backupPackages
    @property
    def clientSettings(self):
        return self._clientSettings
    @property
    def configFile(self):
        return self._configFile
    @property
    def env(self):
        return self._env

    def addPackage (self,package):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(package, backupPackage):
            logger.error("Backup Package  is not of type backupPackage.")
            raise Exception("Backup Package is not of type backupPackage.")
        self._backupPackages.append(package)

        logger.debug("Leaving function "+str(function_name))
        return
    
    def removePackage(self, packageName):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        successFlag=False
        for package in self._backupPackages:
            if package.backupPackageName == packageName:
                self._backupPackages.remove(package)
                logger.info("Package "+packageName+" removed.")
                successFlag=True
        if not successFlag:
            logger.warning("Package "+packageName+" not found.")
        
        logger.debug("Leaving function "+str(function_name))
        return
    
    def getPackage(self, packageName):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        returnPackage=None
        for package in self._backupPackages:
            if package.backupPackageName == packageName:
                logger.info("Package "+packageName+" found.")
                returnPackage=package
                break

        logger.debug("Leaving function "+str(function_name))
        return returnPackage

    def listPackages(self,details=True):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))
        resultDict=[]
        if details:
            logger.info("Listing backup packages:")
            for package in self._backupPackages:
                resultDict.append(package.to_dict())
        else:
            logger.info("Listing backup packages names:")
            for package in self._backupPackages:
                resultDict.append(package._backupPackageName)
        return resultDict
        
    def executePackage(self, packageName=None):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        self.ensureUser()

        if packageName is None:
            logger.error("Package name is not defined.")
            raise ValueError("Package name is not defined.")

        package=self.getPackage(packageName)
        if package is None:
            logger.error("Package "+packageName+" not found.")
            raise ValueError("Package "+packageName+" not found.")
        
        package.execute()
        logger.debug("Leaving function "+str(function_name))
        return 
    
    def execute(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        self.ensureUser()

        for package in self._backupPackages:
            package.execute()

        logger.debug("Leaving function "+str(function_name))
        return
    
    def ensureUser(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        try:
            currentUser=pwd.getpwuid(os.getuid()).pw_name
        except Exception as e:
            logger.error("Cannot determine current user.")
            raise RuntimeError("Cannot determine current user.")

        logger.info("Current user is "+str(currentUser)+".")
        if currentUser == self.backupUser:
            logger.info("Current user is the backup user.")
        else:
            logger.warning("Current user is not the backup user.")
            raise PermissionError
        
        logger.debug("Leaving function "+str(function_name))
        return
        
    def test_backupMountPoint(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if os.stat(self.backupMountPoint) == os.stat(os.path.dirname(self.backupMountPoint)):
            logger.error("Backup mount point "+str(self.backupMountType)+"is not mounted -- it is currently local directory")
            successFlag=False
        else:
            logger.info("Backup mount point "+str(self.backupMountPoint)+" is mounted.")
            successFlag=True

        logger.debug("Leaving function "+str(function_name))
        return successFlag
    
    def mount_backupLocation(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        successFlag=False
        if self.backupMountType == "local" and not self.test_backupMountPoint() and os.path.exists(self._backupMountPoint):            
            logger.info("Backup location "+str(self.backupLocation)+" is a local directory.")
            successFlag=True
        else:
            logger.info("Mounting backup location "+str(self._backupLocation)+".")
            if self._backupMountType == "smb":
                mount_command = "mount -t cifs -o username="+self._backupFileServerUser+",password="+self._backupFileServerPassword+" "+self._backupRemoteHost+" "+self._backupMountPoint
            if self._backupMountType == "nfs":
                mount_command = "mount -t "+self._backupMountType+" "+self._backupRemoteHost+" "+self._backupMountPoint
            os.system(mount_command)
            if os.stat(self._backupMountPoint) == os.stat(os.path.dirname(self._backupMountPoint)):
                logger.error("Backup mount point "+str(self._backupMountType)+" is not mounted -- it is currently local directory")
                successFlag=False
            else:
                logger.info("Backup mount point "+str(self._backupMountType)+" is mounted")
                successFlag=True
        
        logger.debug("Leaving function "+str(function_name))
        return successFlag

    def unmount_backupLocation(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        successFlag=False
        if self._backupMountType == "local" and not self.test_backupMountPoint():
            logger.warning("Backup location "+str(self.backupLocation)+" is a local directory.")
            logger.warning("Backup location "+str(self.backupLocation)+" is a local directory.  It cannot be unmounted.")
            successFlag=False
        else:
            logger.info("Unmounting backup location "+str(self.backupLocation)+".")
            if self.test_backupMountPoint:
                mount_command = "umount "+self.backupMountPoint
                os.system(mount_command)
                if os.stat(self.backupMountPoint) == os.stat(os.path.dirname(self.backupMountPoint)):
                    logger.info("Backup mount point "+str(self.backupMountType)+" has been unmounted -- it is currently local directory")
                    successFlag=True
                else:
                    logger.warning("Backup mount point "+str(self.backupMountType)+" is still mounted")
                    successFlag=False
        
        logger.debug("Leaving function "+str(function_name))
        return successFlag

    def test_backupLocation(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not Path.exists(self.backupLocation):
            try:
                os.makedirs(self.backupLocation)
                os.chown(self.backupLocation,self.backupUser,self.backupUserGroup)
                os.chmod(self.backupLocation,0o750)
                logger.info("Backup location "+str(self.backupLocation)+" created.")
                successFlag=True
            except Exception as e:
                logger.error("Backup location "+str(self.backupLocation)+" could not be created.")
                logger.error(e)
                successFlag=False
        else:
            logger.info("Backup location "+str(self.backupLocation)+" exists.")
            successFlag=True

        logger.debug("Leaving function "+str(function_name))
        return successFlag

    def writeConfig(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        dwlab_IS=dwlabSettings(self.to_dict())
        dwlab_IS.write_yaml(self.configFile)

        logger.debug("Leaving function "+str(function_name))
        return
    
    def to_dict(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        resultDict=dict()
        resultDict["env"]=self.env.to_dict()
        resultDict["clientSettings"]=self.clientSettings.to_dict()
        resultDict["configFile"]=str(self.configFile)
        resultDict["backupPackages"]=[backupPackage.to_dict() for backupPackage in self._backupPackages]

        logger.debug("Leaving function "+str(function_name))
        return resultDict

    @classmethod 
    def from_dict(cls,backupClientDict):
        function_name = sys._getframe().f_code.co_name
        class_name="backupClient"
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(backupClientDict,dict):
            logger.error("backupClientDict is not a dict")
            raise TypeError("backupClientDict is not a dict")

        cls._env=dwlabRuntimeEnvironment.from_dict(backupClientDict.get("env",dict()))
        cls._clientSettings=dwlabSettings(backupClientDict.get("clientSettings",dict()))
        cls._configFile=Path(backupClientDict.get("configFile",""))
        
        backupPackagesDict=backupClientDict.get("backupPackages",[])
        cls._backupPackages=[]
        for backupPackageDict in backupPackagesDict:
            package=backupPackage.from_dict(backupPackageDict.get("backupPackage",dict()))
            cls._backupPackages.append(package)

        logger.debug("Leaving function "+str(function_name))
        return 
    
class backupPackage:
    def __init__(self,
                backupPackageName="",
                backupFrequency="daily",
                backupGenerations=3,
                backupJobs=None
            ):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        self._backupPackageName=backupPackageName
        self._backupFrequency=backupFrequency
        self._backupGenerations=backupGenerations
        self._backupJobs=backupJobs

        if self._backupPackageName=="":
            logger.error("No backup package name given.")
            raise Exception("No backup package name given.")

        logger.debug("Leaving function "+str(function_name))

    @property
    def backupPackageName(self):
        return self._backupPackageName
    
    @property
    def backupFrequency(self):
        return self._backupFrequency
    @backupFrequency.setter
    def backupFrequency(self, value):
        self._backupFrequency = value
    
    @property
    def backupGenerations(self):
        return self._backupGenerations
    @backupGenerations.setter
    def backupGenerations(self, value):
        self._backupGenerations = value

    @property
    def backupJobs(self):
        return self._backupJobs

    def addJob (self,job):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(job,backupJob):
            logger.error("Backup job  is not of type backupJob.")
            raise Exception("Backup job  is not of type backupJob.")
        self._backupJobs.append(job)

        logger.debug("Leaving function "+str(function_name))
        return

    def removeJob (self,job):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(job,backupJob):
            logger.error("Backup job  is not of type backupJob.")
            raise Exception("Backup job  is not of type backupJob.")
        self._backupJobs.remove(job)

        logger.debug("Leaving function "+str(function_name))
        return

    def getJob (self,backupJobName):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        for job  in self.backupJobs:
            if job.backupJobName==backupJobName:
                return job 

        logger.debug("Leaving function "+str(function_name))
        return None
    
    def listJobs (self,details=False):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))
        resultDict=[]
        for job  in self.backupJobs:
            if details:
                resultDict.append(job.to_dict())
            else:
                resultDict.append(job.backupJobName)
        
        return resultDict
    

    def to_dict(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        resultDict=dict()
        resultDict["backupPackageName"]=self._backupPackageName
        resultDict["backupFrequency"]=self._backupFrequency
        resultDict["backupGenerations"]=self._backupGenerations
        resultDict["backupJobs"]=[backupJob.to_dict() for backupJob in self._backupJobs]

        logger.debug("Leaving function "+str(function_name))
        return resultDict
    
    @classmethod 
    def from_dict(cls,dataDict):
        function_name = sys._getframe().f_code.co_name
        class_name="backupPackage"
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(dataDict,dict):
            logger.error("dataDict is not of type dict.")
            raise Exception("dataDict is not of type dict.")

        backupPackageName=dataDict.get("backupPackageName","")
        backupFrequency=dataDict.get("backupFrequency","")
        backupGenerations=dataDict.get("backupGenerations","")
        
        backupJobsArray=dataDict.get("backupJobs",[])
        backupJobs=[]
        for jobDict in backupJobsArray:
            job=backupJob.from_dict(jobDict)
            backupJobs.append(job)

        logger.debug("Leaving function "+str(function_name))
        return cls(
            backupPackageName=backupPackageName,
            backupFrequency=backupFrequency,
            backupGenerations=backupGenerations,
            backupJobs=backupJobs
        )
    
    def execute(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))
        for job in self._backupJobs:
                job.execute()
        logger.debug("Leaving function "+str(function_name))
        return
    
    def schedule(self,backupUser=None):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))
        
        if backupUser is None:
            logger.error("backupUser is not defined.")
            raise Exception("backupUser is not defined.")
        
        # Define the cron schedule based on the backup frequency
        cron_time = {
            "hourly": "0 * * * *",
            "daily": "0 0 * * *",
            "weekly": "0 0 * * 0",
            "monthly": "0 0 1 * *"
        }.get(self._backupFrequency, "0 0 * * *")  # Default to daily if invalid
        
        cron_job = f"{cron_time} dwlab_backupPackage.py {self._backupPackageName}"
        
        try:
            user_cron_file = f"/var/spool/cron/crontabs/{backupUser}"
            
            with open(user_cron_file, "a") as cron_file:
                cron_file.write(cron_job + "\n")
                
            subprocess.run(["crontab", user_cron_file], check=True)
            logger.info(f"Scheduled backup job for {self._backupPackageName} with frequency {self._backupFrequency}")
        
        except Exception as e:
            logger.error(f"Failed to schedule backup job: {str(e)}")
            raise
        
        logger.debug("Leaving function "+str(function_name))
        return

class backupJob:
    def __init__(self,
                backupJobName="",
                backupCommand="",
                backupCommandParameters="",
                backupCommmandUser=""
        ):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        self._backupJobName=backupJobName
        if self._backupJobName=="":
            logger.error("No backup job name given.")
            raise Exception("No backup job name given.")
        
        self._backupCommand=backupCommand
        self._backupCommandParameters=backupCommandParameters
        self._backupCommmandUser=backupCommmandUser

        logger.debug("Leaving function "+str(function_name))


    @property
    def backupJobName(self):
        return self._backupJobName
    @backupJobName.setter
    def backupJobName(self, value):
        self._backupJobName = value
    
    @property
    def backupCommand(self):
        return self._backupCommand
    @backupCommand.setter
    def backupCommand(self, value):
        self._backupCommand = value
    
    @property
    def backupCommandParameters(self):
        return self._backupCommandParameters
    @backupCommandParameters.setter
    def backupCommandParameters(self, value):
        self._backupCommandParameters = value

    
    def to_dict(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        resultDict=dict()
        resultDict["backupJobName"]=self._backupJobName
        resultDict["backupCommand"]=self._backupCommand
        resultDict["backupCommandParameters"]=self._backupCommandParameters
        resultDict["backupCommmandUser"]=self._backupCommmandUser

        logger.debug("Leaving function "+str(function_name))
        return resultDict
    
    @classmethod
    def from_dict(cls,dataDict):
        function_name = sys._getframe().f_code.co_name
        class_name="backupJob"
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        if not isinstance(dataDict,dict):
            logger.error("Data is not a dict")
            raise Exception("Data is not a dict")

        backupJobName=dataDict.get("backupJobName","")
        backupCommand=dataDict.get("backupCommand","")
        backupCommandParameters=dataDict.get("backupCommandParameters","")
        backupCommmandUser=dataDict.get("backupCommmandUser","")

        logger.debug("Leaving function "+str(function_name))
        return cls(
            backupJobName=backupJobName,
            backupCommand=backupCommand,
            backupCommandParameters=backupCommandParameters,
            backupCommmandUser=backupCommmandUser
        )

    def execute(self):
        function_name = sys._getframe().f_code.co_name
        class_name=self.__class__.__name__
        function_name=class_name+"."+function_name
        logger.debug("Entering function "+str(function_name))

        logger.info("Executing backup job "+self._backupJobName)
        command=self._backupCommand+" "+self._backupCommandParameters
        if self._backupCommmandUser!="":
            command="sudo -u "+self._backupCommmandUser+" "+command
        
        logger.info("Executing command: "+command)

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            returnDict = {
                "success": True,
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except subprocess.CalledProcessError as e:
            returnDict = {
                "success": False,
                "return_code": e.returncode,
                "stdout": e.stdout.strip() if e.stdout else "",
                "stderr": e.stderr.strip() if e.stderr else "Command failed",
            }

        logger.debug("Leaving function "+str(function_name))
        return returnDict
    