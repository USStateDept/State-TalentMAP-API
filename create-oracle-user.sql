ALTER SESSION SET CONTAINER = talentmappdb;
GRANT connect, resource to talentmap1 identified by talentmap1 container=current;
GRANT CREATE SESSION TO talentmap1 container=current;
GRANT ALL PRIVILEGES TO talentmap1;
