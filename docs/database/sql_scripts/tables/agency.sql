CREATE TABLE `Agency` (
  `AgencyID` varchar(50) NOT NULL,
  `AgencyName` varchar(255) NOT NULL,
  `AgencyURL` varchar(255) NOT NULL,
  `AgencyTimezone` varchar(50) NOT NULL,
  `AgencyLang` varchar(2) NOT NULL,
  `AgencyPhone` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`AgencyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
