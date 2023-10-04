CREATE DATABASE  IF NOT EXISTS `coco` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE DATABASE  IF NOT EXISTS `room`;
USE `coco`;
-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: coco
-- ------------------------------------------------------
-- Server version	8.0.33-0ubuntu0.20.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alarm`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `alarm` (
  `id` int NOT NULL AUTO_INCREMENT,
  `receiver` varchar(45) DEFAULT NULL,
  `sender` varchar(45) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `context` json DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `category` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `boards`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `boards` (
  `id` int NOT NULL AUTO_INCREMENT,
  `context` mediumtext,
  `title` text,
  `rel_task` int DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `category` tinyint DEFAULT NULL,
  `likes` smallint DEFAULT '0',
  `views` smallint DEFAULT '0',
  `comments` smallint DEFAULT '0',
  `code` longtext,
  PRIMARY KEY (`id`),
  KEY `FK_rel` (`rel_task`),
  CONSTRAINT `FK_rel_task` FOREIGN KEY (`rel_task`) REFERENCES `task` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `boards_ids`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `boards_ids` (
  `board_id` int NOT NULL,
  `user_id` varchar(45) NOT NULL,
  PRIMARY KEY (`board_id`,`user_id`),
  KEY `FK_boards_ids2_idx` (`user_id`),
  CONSTRAINT `FK_boards_ids1` FOREIGN KEY (`board_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_boards_ids2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `boards_likes`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `boards_likes` (
  `user_id` varchar(45) NOT NULL,
  `boards_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`boards_id`),
  KEY `FK_board_likes1_idx` (`boards_id`),
  CONSTRAINT `FK_boards_likes2` FOREIGN KEY (`boards_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `context` text,
  `write_time` datetime DEFAULT NULL,
  `likes` mediumint DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments_ids`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `comments_ids` (
  `comment_id` int NOT NULL,
  `user_id` varchar(45) NOT NULL,
  `board_id` int NOT NULL,
  PRIMARY KEY (`comment_id`,`user_id`,`board_id`),
  KEY `FK_comments_id2_idx` (`user_id`),
  KEY `FK_comments_id3` (`board_id`),
  CONSTRAINT `FK_comments_id1` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_comments_id2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `FK_comments_id3` FOREIGN KEY (`board_id`) REFERENCES `boards` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments_likes`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `comments_likes` (
  `user_id` varchar(45) NOT NULL,
  `comment_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`comment_id`),
  KEY `FK_comments_likes2_idx` (`comment_id`),
  CONSTRAINT `FK_comments_likes1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `FK_comments_likes2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `descriptions`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `descriptions` (
  `task_id` int NOT NULL,
  `main` text,
  `in` text,
  `out` text,
  PRIMARY KEY (`task_id`),
  CONSTRAINT `FK_desc_task` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `my_tasks`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `my_tasks` (
  `user_id` varchar(45) NOT NULL,
  `task_num` int NOT NULL,
  `solved` tinyint DEFAULT NULL,
  PRIMARY KEY (`user_id`,`task_num`),
  KEY `FK_mytasks_task` (`task_num`),
  CONSTRAINT `FK_mytasks_task` FOREIGN KEY (`task_num`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_mytasks_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `room`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `room` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `desc` mediumtext,
  `leader` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `room_ids`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `room_ids` (
  `room_id` int NOT NULL,
  `user_id` varchar(45) NOT NULL,
  PRIMARY KEY (`room_id`,`user_id`),
  KEY `FK_user_id_idx` (`user_id`),
  KEY `FK_group_id_idx` (`room_id`),
  CONSTRAINT `FK_room_id` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `status_all`
--

DROP TABLE IF EXISTS `status_all`;
/*!50001 DROP VIEW IF EXISTS `status_all`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `status_all` AS SELECT 
 1 AS `sub_id`,
 1 AS `user_id`,
 1 AS `task_id`,
 1 AS `status`,
 1 AS `time`,
 1 AS `lang`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `status_list`
--

DROP TABLE IF EXISTS `status_list`;
/*!50001 DROP VIEW IF EXISTS `status_list`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `status_list` AS SELECT 
 1 AS `sub_id`,
 1 AS `user_id`,
 1 AS `task_id`,
 1 AS `title`,
 1 AS `lang`,
 1 AS `status`,
 1 AS `time`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `sub_ids`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `sub_ids` (
  `user_id` varchar(45) NOT NULL,
  `task_id` int NOT NULL,
  `sub_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`task_id`,`sub_id`),
  KEY `FK_sub_ids3_idx` (`sub_id`),
  KEY `FK_sub_ids2` (`task_id`),
  CONSTRAINT `FK_sub_ids1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_sub_ids2` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_sub_ids3` FOREIGN KEY (`sub_id`) REFERENCES `submissions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `sub_per_task`
--

DROP TABLE IF EXISTS `sub_per_task`;
/*!50001 DROP VIEW IF EXISTS `sub_per_task`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `sub_per_task` AS SELECT 
 1 AS `task_id`,
 1 AS `count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `submissions`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status_id` int DEFAULT NULL,
  `code` text,
  `stdout` text,
  `time` datetime DEFAULT NULL,
  `stderr` text,
  `token` varchar(45) DEFAULT NULL,
  `callback_url` varchar(45) DEFAULT NULL,
  `exit_code` int DEFAULT NULL,
  `message` varchar(45) DEFAULT NULL,
  `number_of_runs` tinyint DEFAULT NULL,
  `status` tinyint DEFAULT NULL,
  `lang` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(45) NOT NULL,
  `sample` json NOT NULL,
  `rate` float DEFAULT '0',
  `mem_limit` mediumint NOT NULL,
  `time_limit` tinyint NOT NULL,
  `diff` tinyint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_category`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS`task_category` (
  `category` varchar(45) NOT NULL,
  PRIMARY KEY (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_ids`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `task_ids` (
  `task_id` int NOT NULL,
  `category` varchar(45) NOT NULL,
  PRIMARY KEY (`task_id`,`category`),
  KEY `FK_task_category_idx` (`category`),
  CONSTRAINT `FK_task_ids1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_task_ids2` FOREIGN KEY (`category`) REFERENCES `task_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `task_list`
--

DROP TABLE IF EXISTS `task_list`;
/*!50001 DROP VIEW IF EXISTS `task_list`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `task_list` AS SELECT 
 1 AS `id`,
 1 AS `title`,
 1 AS `diff`,
 1 AS `rate`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `task_title`
--

DROP TABLE IF EXISTS `task_title`;
/*!50001 DROP VIEW IF EXISTS `task_title`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `task_title` AS SELECT 
 1 AS `id`,
 1 AS `title`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `user` (
  `id` varchar(45) NOT NULL,
  `pw` varchar(60) NOT NULL,
  `name` varchar(10) NOT NULL,
  `role` int DEFAULT '0',
  `email` varchar(45) NOT NULL,
  `exp` int DEFAULT '0',
  `tutor` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `user_problem`
--

DROP TABLE IF EXISTS `user_problem`;
/*!50001 DROP VIEW IF EXISTS `user_problem`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `user_problem` AS SELECT 
 1 AS `user_id`,
 1 AS `task_id`,
 1 AS `sub_id`,
 1 AS `status`,
 1 AS `message`,
 1 AS `time`,
 1 AS `diff`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_tutor`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `user_tutor` (
  `user_id` varchar(45) NOT NULL,
  `reason` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `FK_user_tutor` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `view_board`
--

DROP TABLE IF EXISTS `view_board`;
/*!50001 DROP VIEW IF EXISTS `view_board`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_board` AS SELECT 
 1 AS `id`,
 1 AS `title`,
 1 AS `time`,
 1 AS `category`,
 1 AS `likes`,
 1 AS `views`,
 1 AS `comments`,
 1 AS `user_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_task`
--

DROP TABLE IF EXISTS `view_task`;
/*!50001 DROP VIEW IF EXISTS `view_task`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_task` AS SELECT 
 1 AS `id`,
 1 AS `title`,
 1 AS `diff`,
 1 AS `rate`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `wpc`
--


/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE IF NOT EXISTS `wpc` (
  `sub_id` int NOT NULL,
  `status` tinyint NOT NULL,
  `result` text,
  PRIMARY KEY (`sub_id`),
  CONSTRAINT `FK_wpc_sub` FOREIGN KEY (`sub_id`) REFERENCES `submissions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `status_all`
--

/*!50001 DROP VIEW IF EXISTS `status_all`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `status_all` AS select `s_ids`.`sub_id` AS `sub_id`,`s_ids`.`user_id` AS `user_id`,`s_ids`.`task_id` AS `task_id`,`s`.`status` AS `status`,`s`.`time` AS `time`,`s`.`lang` AS `lang` from (`submissions` `s` join `sub_ids` `s_ids`) where (`s`.`id` = `s_ids`.`sub_id`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `status_list`
--

/*!50001 DROP VIEW IF EXISTS `status_list`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `status_list` AS select `i`.`sub_id` AS `sub_id`,`i`.`user_id` AS `user_id`,`i`.`task_id` AS `task_id`,`t`.`title` AS `title`,`s`.`lang` AS `lang`,`s`.`status` AS `status`,`s`.`time` AS `time` from ((`submissions` `s` join `task` `t`) join `sub_ids` `i`) where ((`s`.`id` = `i`.`sub_id`) and (`i`.`task_id` = `t`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `sub_per_task`
--

/*!50001 DROP VIEW IF EXISTS `sub_per_task`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `sub_per_task` AS select `sub_ids`.`task_id` AS `task_id`,count(0) AS `count` from `sub_ids` group by `sub_ids`.`task_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `task_list`
--

/*!50001 DROP VIEW IF EXISTS `task_list`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `task_list` AS select `t`.`id` AS `id`,`t`.`title` AS `title`,`t`.`diff` AS `diff`,`t`.`rate` AS `rate` from `task` `t` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `task_title`
--

/*!50001 DROP VIEW IF EXISTS `task_title`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `task_title` AS select `task`.`id` AS `id`,`task`.`title` AS `title` from `task` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `user_problem`
--

/*!50001 DROP VIEW IF EXISTS `user_problem`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `user_problem` AS select `ids`.`user_id` AS `user_id`,`ids`.`task_id` AS `task_id`,`ids`.`sub_id` AS `sub_id`,`sub`.`status` AS `status`,`sub`.`message` AS `message`,date_format(`sub`.`time`,'%y%m') AS `time`,`t`.`diff` AS `diff` from ((`sub_ids` `ids` join `submissions` `sub`) join `task` `t`) where ((`sub`.`id` = `ids`.`sub_id`) and (`ids`.`task_id` = `t`.`id`)) order by `ids`.`user_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_board`
--

/*!50001 DROP VIEW IF EXISTS `view_board`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_board` AS select `b`.`id` AS `id`,`b`.`title` AS `title`,`b`.`time` AS `time`,`b`.`category` AS `category`,`b`.`likes` AS `likes`,`b`.`views` AS `views`,`b`.`comments` AS `comments`,`i`.`user_id` AS `user_id` from (`boards` `b` join `boards_ids` `i`) where (`b`.`id` = `i`.`board_id`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_task`
--

/*!50001 DROP VIEW IF EXISTS `view_task`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_task` AS select `task`.`id` AS `id`,`task`.`title` AS `title`,`task`.`diff` AS `diff`,`task`.`rate` AS `rate` from `task` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-10-02 20:18:09
