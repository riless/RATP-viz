-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Client: localhost
-- Généré le: Mer 03 Juin 2015 à 18:47
-- Version du serveur: 5.5.43-0ubuntu0.14.04.1
-- Version de PHP: 5.5.9-1ubuntu4.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de données: `pldac`
--

-- --------------------------------------------------------

--
-- Structure de la table `agency`
--

CREATE TABLE IF NOT EXISTS `agency` (
  `agency_id` int(12) NOT NULL AUTO_INCREMENT,
  `agency_name` varchar(255) NOT NULL,
  `agency_url` varchar(255) DEFAULT NULL,
  `agency_timezone` varchar(100) DEFAULT NULL,
  `agency_lang` varchar(100) DEFAULT NULL,
  `agency_phone` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`agency_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=101 ;

-- --------------------------------------------------------

--
-- Structure de la table `arrondissements`
--

CREATE TABLE IF NOT EXISTS `arrondissements` (
  `arr_cp` varchar(6) NOT NULL,
  `code_insee` varchar(20) NOT NULL,
  `arr_name` varchar(100) NOT NULL,
  `arr_geo` varchar(1000) NOT NULL,
  `barycentre_lon` varchar(100) NOT NULL,
  `barycentre_lat` varchar(100) NOT NULL,
  PRIMARY KEY (`arr_cp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `calendar`
--

CREATE TABLE IF NOT EXISTS `calendar` (
  `service_id` int(12) NOT NULL AUTO_INCREMENT,
  `monday` tinyint(1) DEFAULT NULL,
  `tuesday` tinyint(1) DEFAULT NULL,
  `wednesday` tinyint(1) DEFAULT NULL,
  `thursday` tinyint(1) DEFAULT NULL,
  `friday` tinyint(1) DEFAULT NULL,
  `saturday` tinyint(1) DEFAULT NULL,
  `sunday` tinyint(1) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11874879 ;

-- --------------------------------------------------------

--
-- Structure de la table `calendar_dates`
--

CREATE TABLE IF NOT EXISTS `calendar_dates` (
  `service_id` int(12) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `exception_type` tinyint(2) NOT NULL,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11874879 ;

-- --------------------------------------------------------

--
-- Structure de la table `colors`
--

CREATE TABLE IF NOT EXISTS `colors` (
  `color_id` int(11) NOT NULL AUTO_INCREMENT,
  `color_name` varchar(30) NOT NULL,
  `color_hex` varchar(30) NOT NULL,
  `color_rvb` varchar(30) NOT NULL,
  PRIMARY KEY (`color_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=17 ;

-- --------------------------------------------------------

--
-- Structure de la table `data`
--

CREATE TABLE IF NOT EXISTS `data` (
  `data_cp` varchar(5) NOT NULL,
  `data_value` double NOT NULL,
  `data_id` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `data_meta`
--

CREATE TABLE IF NOT EXISTS `data_meta` (
  `data_id` varchar(100) NOT NULL,
  `data_label` varchar(100) NOT NULL,
  `data_icon` varchar(100) NOT NULL,
  PRIMARY KEY (`data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `flux_passagers`
--

CREATE TABLE IF NOT EXISTS `flux_passagers` (
  `from_cp` varchar(255) NOT NULL,
  `to_cp` varchar(255) NOT NULL,
  `value` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `lignes`
--

CREATE TABLE IF NOT EXISTS `lignes` (
  `route_short_name` varchar(50) NOT NULL,
  `stop_before` int(11) NOT NULL,
  `stop_after` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `lines_colors`
--

CREATE TABLE IF NOT EXISTS `lines_colors` (
  `route_short_name` varchar(50) NOT NULL,
  `color_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `passages`
--

CREATE TABLE IF NOT EXISTS `passages` (
  `usager_id` varchar(20) NOT NULL,
  `passage_time` varchar(20) NOT NULL,
  `stop_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `routes`
--

CREATE TABLE IF NOT EXISTS `routes` (
  `route_id` int(12) NOT NULL AUTO_INCREMENT,
  `agency_id` int(12) DEFAULT NULL,
  `route_short_name` varchar(50) DEFAULT NULL,
  `route_long_name` varchar(255) DEFAULT NULL,
  `route_type` varchar(2) DEFAULT NULL,
  `route_text_color` varchar(7) DEFAULT NULL,
  `route_color` varchar(7) DEFAULT NULL,
  `route_url` varchar(255) DEFAULT NULL,
  `route_desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`route_id`),
  KEY `agency_id` (`agency_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1197660 ;

-- --------------------------------------------------------

--
-- Structure de la table `stops`
--

CREATE TABLE IF NOT EXISTS `stops` (
  `stop_id` int(12) NOT NULL,
  `stop_code` varchar(50) DEFAULT NULL,
  `stop_name` varchar(255) DEFAULT NULL,
  `stop_desc` varchar(255) DEFAULT NULL,
  `stop_lat` double DEFAULT NULL,
  `stop_lon` double DEFAULT NULL,
  `zone_id` varchar(255) DEFAULT NULL,
  `stop_url` varchar(255) DEFAULT NULL,
  `location_type` varchar(2) DEFAULT NULL,
  `parent_station` int(12) DEFAULT NULL,
  `stop_timezone` varchar(50) DEFAULT NULL,
  `wheelchair_boarding` tinyint(1) DEFAULT NULL,
  `stop_cp` varchar(5) NOT NULL,
  PRIMARY KEY (`stop_id`),
  KEY `zone_id` (`zone_id`),
  KEY `parent_station` (`parent_station`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `stop_times`
--

CREATE TABLE IF NOT EXISTS `stop_times` (
  `trip_id` bigint(20) DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `arrival_time_seconds` int(100) DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `departure_time_seconds` int(100) DEFAULT NULL,
  `stop_id` int(12) DEFAULT NULL,
  `stop_sequence` int(12) DEFAULT NULL,
  `stop_headsign` varchar(50) DEFAULT NULL,
  `pickup_type` varchar(2) DEFAULT NULL,
  `drop_off_type` varchar(2) DEFAULT NULL,
  `shape_dist_traveled` varchar(50) DEFAULT NULL,
  KEY `trip_id` (`trip_id`),
  KEY `stop_id` (`stop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `transfers`
--

CREATE TABLE IF NOT EXISTS `transfers` (
  `from_stop_id` int(12) NOT NULL,
  `to_stop_id` int(12) NOT NULL,
  `transfer_type` tinyint(1) NOT NULL,
  `min_transfer_time` int(12) DEFAULT NULL,
  KEY `from_stop_id` (`from_stop_id`),
  KEY `to_stop_id` (`to_stop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `transfers_lignes`
--

CREATE TABLE IF NOT EXISTS `transfers_lignes` (
  `from_stop_name` varchar(255) NOT NULL,
  `to_route_short_name` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `transfers_routes`
--

CREATE TABLE IF NOT EXISTS `transfers_routes` (
  `stop_id` int(11) NOT NULL,
  `route_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `trips`
--

CREATE TABLE IF NOT EXISTS `trips` (
  `route_id` int(12) DEFAULT NULL,
  `service_id` int(12) DEFAULT NULL,
  `trip_id` bigint(20) DEFAULT NULL,
  `trip_headsign` varchar(255) DEFAULT NULL,
  `trip_short_name` varchar(255) DEFAULT NULL,
  `direction_id` tinyint(1) DEFAULT NULL,
  `block_id` varchar(11) DEFAULT NULL,
  `shape_id` varchar(11) DEFAULT NULL,
  `wheelchair_accessible` tinyint(1) DEFAULT NULL,
  `bikes_allowed` tinyint(1) DEFAULT NULL,
  KEY `route_id` (`route_id`),
  KEY `trip_id` (`trip_id`),
  KEY `service_id` (`service_id`),
  KEY `direction_id` (`direction_id`),
  KEY `block_id` (`block_id`),
  KEY `shape_id` (`shape_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
