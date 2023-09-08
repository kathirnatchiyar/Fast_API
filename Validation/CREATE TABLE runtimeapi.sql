CREATE TABLE runtimeapi (
  custownerid INT NOT NULL,
  customername VARCHAR(100) NOT NULL,
  customertype VARCHAR(100) NOT NULL,
  sessionuser VARCHAR(100) NOT NULL,
  lob VARCHAR(100) NOT NULL,
  transdb VARCHAR(100) NOT NULL,
  uiux VARCHAR(100) NOT NULL,
  workflow VARCHAR(100) NOT NULL,
  rating VARCHAR(100) NOT NULL,
  PRIMARY KEY (custownerid)
);

CREATE USER 'root'@'%' IDENTIFIED BY 'redhat';
GRANT ALL ON *.* TO 'root'@'%';

CREATE TABLE runtimeapi1 (
  ownerid INT NOT NULL,
  customername VARCHAR(100) NOT NULL,
  customertype VARCHAR(100) NOT NULL,
  sessionUser VARCHAR(100) NOT NULL,
  lob VARCHAR(100) NOT NULL,
  transdb VARCHAR(100) NOT NULL,
  uiux VARCHAR(100) NOT NULL,
  workflow VARCHAR(100) NOT NULL,
  rating VARCHAR(100) NOT NULL,
  reportingdb VARCHAR(100) NOT NULL,
  PRIMARY KEY (ownerid)
);