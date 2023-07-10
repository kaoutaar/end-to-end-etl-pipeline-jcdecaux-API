
CREATE DATABASE velib
GO
USE velib
GO


CREATE TABLE Contracts(
    Cont_name VARCHAR(25) UNIQUE NOT NULL,
    Commercial_name VARCHAR(25),
    Country_code VARCHAR(10), 
    CONSTRAINT PK_Contracts_Contract_ID PRIMARY KEY(Cont_name)
)
GO


CREATE TABLE Stations(
    Station_ID INT IDENTITY(1,1) NOT NULL,
    Cont_name VARCHAR(25),
    Station_name VARCHAR(100),
    Station_address VARCHAR(200),
    Banking BIT,
    Bonus BIT,
    Latitude FLOAT,
    Longitude FLOAT,
    CONSTRAINT PK_Stations_Station_ID PRIMARY KEY(Station_ID),
    CONSTRAINT FK_Stations_Contract_ID FOREIGN KEY(Cont_name) REFERENCES Contracts(Cont_name)
    ON DELETE CASCADE
    ON UPDATE CASCADE
)
GO



CREATE TABLE ActivityDate(
    Date_ID BIGINT NOT NULL UNIQUE check(Date_ID>0),
    Year_ INT,
    Month_ INT,
    Day_ INT,
    DayName INT,
    Hour_ INT
)
GO


CREATE TABLE BusinessFact(
    OUT_Bikes INT,
    IN_Bikes INT,
    Station_status VARCHAR(25),
    Capacity INT,
    Date_ID BIGINT NOT NULL,
    Station_ID INT NOT NULL,
    Cont_name VARCHAR(25) NOT NULL,
    CONSTRAINT PK_BusinessFact_ID PRIMARY KEY(Date_ID, Station_ID, Cont_name),
    CONSTRAINT FK_BusinessFact_Date_ID FOREIGN KEY(Date_ID) REFERENCES Activity_Date(Date_ID)
	ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_BusinessFact_Station_ID FOREIGN KEY(Station_ID) REFERENCES Stations(Station_ID)
	ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_BusinessFact_Contract_ID FOREIGN KEY(Cont_name) REFERENCES Contracts(Cont_name)
	ON DELETE NO ACTION
)
GO