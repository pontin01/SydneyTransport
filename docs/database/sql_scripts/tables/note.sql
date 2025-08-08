CREATE TABLE `Note` (
  `NoteID` varchar(50) NOT NULL,
  `NoteText` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`NoteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
