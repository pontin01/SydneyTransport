CREATE TABLE `Shape` (
  `ShapeID` varchar(50) NOT NULL,
  `ShapePtLat` double DEFAULT NULL,
  `ShapePtLon` double DEFAULT NULL,
  `ShapePtSequence` smallint NOT NULL,
  `ShapeDistTraveled` double DEFAULT NULL,
  PRIMARY KEY (`ShapeID`,`ShapePtSequence`),
  KEY `ShapeLat` (`ShapePtLat`,`ShapeID`,`ShapePtSequence`),
  KEY `ShapeLon` (`ShapePtLon`,`ShapeID`,`ShapePtSequence`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
