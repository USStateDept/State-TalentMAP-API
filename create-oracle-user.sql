ALTER SESSION SET CONTAINER = orclpdb1;
GRANT connect, resource to talentmap identified by talentmap container=current;
GRANT CREATE SESSION TO talentmap container=current;
GRANT ALL PRIVILEGES TO TALENTMAP;
