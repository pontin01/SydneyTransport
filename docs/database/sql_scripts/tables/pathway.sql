CREATE TABLE `Pathway` (
  `PathwayID` varchar(255) NOT NULL,
  `FromStopID` varchar(50) DEFAULT NULL,
  `ToStopID` varchar(50) DEFAULT NULL,
  `PathwayMode` tinyint DEFAULT NULL,
  `IsBidirectional` bit(1) DEFAULT NULL,
  `TraversalTime` smallint DEFAULT NULL,
  PRIMARY KEY (`PathwayID`),
  KEY `FromStopID` (`FromStopID`),
  KEY `ToStopID` (`ToStopID`),
  CONSTRAINT `Pathway_ibfk_1` FOREIGN KEY (`FromStopID`) REFERENCES `Stop` (`StopID`),
  CONSTRAINT `Pathway_ibfk_2` FOREIGN KEY (`ToStopID`) REFERENCES `Stop` (`StopID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
