-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 19, 2024 at 01:34 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `event_management_system`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `CancelBooking` (IN `booking_id` INT, IN `user_id` INT)   BEGIN
    DELETE FROM bookings WHERE id = booking_id AND user_id = user_id;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `ticket_id` int(11) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp(),
  `number_of_tickets` int(11) NOT NULL,
  `total_price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `event_id`, `ticket_id`, `date`, `number_of_tickets`, `total_price`) VALUES
(123, 9, 73, 6153, '2024-03-12 01:37:41', 2, 4000.00),
(124, 9, 74, 6154, '2024-03-12 01:38:15', 2, 200.00),
(125, 9, 82, 6188, '2024-03-12 01:38:34', 1, 900.00),
(126, 9, 84, 6195, '2024-03-12 01:38:54', 1, 800.00),
(127, 9, 91, 6222, '2024-03-12 01:39:11', 1, 400.00),
(128, 9, 64, 6241, '2024-03-12 01:43:15', 1, 1500.00),
(129, 9, 65, 6121, '2024-03-17 21:57:15', 1, 750.00);

--
-- Triggers `bookings`
--
DELIMITER $$
CREATE TRIGGER `update_available_tickets` AFTER DELETE ON `bookings` FOR EACH ROW BEGIN
  UPDATE tickets
  SET available_tickets = available_tickets + OLD.number_of_tickets
  WHERE id = OLD.ticket_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `venue` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  `end` datetime NOT NULL,
  `description` text NOT NULL,
  `category_id` int(11) NOT NULL,
  `moredetails` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`id`, `name`, `venue`, `date`, `end`, `description`, `category_id`, `moredetails`) VALUES
(64, 'RockFest India', 'Mumbai Arena', '2024-03-15 18:00:00', '2024-03-15 23:59:00', ' Electrifying rock performances by top bands from around the country.', 1, '    General: Access to the main concert area.\n    VIP: Exclusive access to a VIP lounge, complimentary drinks, and meet-and-greet with artists.\n    VVIP: All VIP perks plus backstage access.\n    Platinum: Ultimate concert experience with front-row seating and personalized memorabilia.'),
(65, 'Bollywood Beats Live', 'Delhi Amphitheatre', '2024-05-01 14:00:00', '2024-05-01 11:59:00', 'A musical extravaganza celebrating Bollywood hits with renowned artists.', 1, '    Regular: Standard access to the concert venue.\r\n    VIP: Reserved seating closer to the stage, exclusive merchandise.\r\n    Platinum: VIP perks plus a backstage tour.\r\n    Gold: Premium seating with complimentary refreshments.'),
(66, 'EDM Fusion Night', 'Bangalore Outdoor Stadium', '2024-07-10 18:00:00', '2024-07-11 06:00:00', 'Energetic night with electronic dance music from top DJs.', 1, '    Standard Pass: Access to all general areas and stages.\r\n    VIP Pass: Exclusive lounge access, express entry, and a festival swag bag.\r\n    Exclusive: VIP perks plus a meet-and-greet with one of the headlining artists.\r\n    Platinum Pass: All-access pass with backstage access, artist interaction, and premium merchandise.'),
(67, 'Jazz in the Garden', 'Pune Botanical Gardens', '2024-09-15 18:00:00', '2024-09-15 23:59:00', ' Evening of smooth jazz under the stars with local and international talent.', 1, '    Jazz Enthusiast: Access to the jazz performances and open seating.\r\n    Standard Jazz: Reserved seating, complimentary refreshments.\r\n    VIP Jazz Lounge: Exclusive lounge access, premium seating, and a jazz-themed gift bag.\r\n    Platinum Jazz Experience: VIP perks plus a backstage tour.'),
(68, 'Indie Music Showcase', 'Kolkata Warehouse', '2024-03-10 00:00:00', '2024-03-10 00:00:00', 'Showcase of independent music talent spanning various genres.', 1, '    Indie Insider: Access to exclusive artist Q&A session and limited edition merchandise.\r\n    General Indie: Standing room access to the indie music showcase.\r\n    VIP Indie Lounge: VIP perks plus backstage access.\r\n    Platinum Indie Experience: All-access pass with front-row seating and a personalized souvenir.'),
(69, 'Classical Serenade', 'Chennai Symphony Hall', '2024-01-15 18:00:00', '2024-01-15 23:59:00', 'Night of classical music featuring maestros in Indian and Western traditions.', 1, '    Maestro Pass: Access to exclusive lounge areas and a guided tour.\r\n    Classical Enthusiast: Premium seating with a dedicated usher.\r\n    VIP Symphony Lounge: VIP perks plus a meet-and-greet with the featured maestros.\r\n    Platinum Classical Experience: All-access pass with backstage access and personalized memorabilia.'),
(70, 'Pop Sensation Night', 'Hyderabad Arena', '2024-04-01 17:00:00', '2024-04-01 23:59:00', 'Pop music extravaganza with chart-topping artists.', 1, '    General Pop Pass: Access to the main concert area.\r\n    VIP Pop Lounge: VIP perks plus exclusive backstage access.\r\n    Platinum Pop Experience: All-access pass with front-row seating and personalized memorabilia.\r\n    Ultimate Pop Fan Package: VIP perks plus a private meet-and-greet with one of the headlining artists.'),
(71, 'Fusion Beats Live', 'Jaipur Cultural Center', '2024-05-10 10:00:00', '2024-05-10 23:59:00', 'Fusion music event featuring a blend of traditional and contemporary sounds.', 1, '    Standard Fusion Pass: Access to the main concert area.\r\n    VIP Fusion Lounge: VIP perks plus exclusive backstage access.\r\n    Platinum Fusion Experience: All-access pass with front-row seating and personalized memorabilia.\r\n    Ultimate Fusion Fan Package: VIP perks plus a private meet-and-greet with one of the headlining artists.'),
(72, 'Country Vibes Live', 'Bangalore Open Air Theatre', '2024-07-20 16:00:00', '2024-07-20 22:00:00', 'Night of country music featuring top country artists.', 1, '    Country Fan Pass: Access to the main concert area.\r\n    VIP Country Lounge: VIP perks plus exclusive backstage access.\r\n    Platinum Country Experience: All-access pass with front-row seating and personalized memorabilia.\r\n    Ultimate Country Fan Package: VIP perks plus a private meet-and-greet with one of the headlining artists.'),
(73, 'Reggae Rhythms Festival', 'Goa Reggae Beach', '2024-09-05 06:00:00', '2024-09-06 23:59:00', 'Festival celebrating reggae music with a beachside vibe.', 1, '    Standard Reggae Pass: Access to the main concert area.\r\n    VIP Reggae Lounge: VIP perks plus exclusive backstage access.\r\n    Platinum Reggae Experience: All-access pass with front-row seating and personalized memorabilia.\r\n    Ultimate Reggae Fan Package: VIP perks plus a private meet-and-greet with one of the headlining artists.'),
(74, 'Holi Fiesta Extravaganza', 'Jaipur Festival Grounds', '2024-03-15 06:00:00', '2024-03-15 23:59:00', 'Vibrant Holi celebration with live music, traditional dance, and festive colors.', 2, '    General Holi Pass: Access to the main festival grounds.\r\n    VIP Holi Lounge: VIP perks plus exclusive access to a designated VIP area.\r\n    Platinum Holi Experience: VIP perks plus a guided tour of festival highlights.\r\n    Ultimate Holi Fan Package: VIP perks plus a private area with additional amenities.'),
(75, 'Diwali Spectacle', 'Mumbai Cultural Park', '2024-11-01 10:00:00', '2024-11-01 18:00:00', 'Grand Diwali celebration with cultural performances, fireworks, and culinary delights.', 2, '    Diwali Enthusiast: Access to cultural displays and light installations.\r\n    VIP Illumination Pass: VIP perks plus guided tour of illuminated exhibits.\r\n    Diwali VIP Lounge: VIP perks plus exclusive lounge access and culinary delights.\r\n    Platinum Diwali Experience: VIP perks plus front-row seating and a Diwali-themed gift.'),
(76, 'Navratri Dandiya Night', 'Ahmedabad Cultural Hall', '2024-10-01 06:00:00', '2024-10-01 23:00:00', 'Traditional Dandiya dance night with lively music and colorful attire.', 2, '    Dandiya Dancer: Access to the dandiya dance floor.\r\n    Navratri VIP Pass: VIP perks plus complimentary dandiya sticks.\r\n    Exclusive Dandiya Lounge: VIP perks plus exclusive lounge access and traditional attire.\r\n    Platinum Navratri Experience: VIP perks plus front-row seating and a Navratri-themed gift.'),
(77, 'Ganesh Chaturthi Extravaganza', 'Mumbai Cultural Park', '2024-08-25 06:00:00', '2024-08-25 23:59:00', 'Cultural extravaganza celebrating the festival of Lord Ganesha with music and dance.', 2, '    Cultural Devotee: Access to cultural performances and exhibits.\r\n    Ganesh Darshan Pass: VIP perks plus exclusive access to a dedicated area near the idol.\r\n    Exclusive Cultural Lounge: VIP perks plus guided tour and a cultural gift.\r\n    Platinum Ganesh Experience: VIP perks plus front-row seating and a personalized souvenir.'),
(78, 'Eid Celebration Bazaar', 'Hyderabad Cultural Center', '2024-05-15 09:00:00', '2024-05-15 21:00:00', ' Grand bazaar celebrating the festival of Eid with traditional music, food, and shopping.', 2, '    Eid Shopper Pass: Access to the grand Eid celebration bazaar.\r\n    VIP Eid Experience: VIP perks plus a guided shopping tour.\r\n    Exclusive Shopping Lounge: VIP perks plus access to an exclusive shopping lounge.\r\n    Platinum Eid Extravaganza: VIP perks plus front-row seating at the cultural performances.'),
(79, 'Navratri Garba Night', 'Ahmedabad Cultural Hall', '2024-10-02 18:00:00', '2024-10-02 23:59:00', 'Traditional Garba dance night with vibrant music and colorful attire.', 2, '    Garba Enthusiast: Access to the Garba dance floor.\r\n    Navratri VIP Pass: VIP perks plus complimentary Garba sticks.\r\n    Exclusive Garba Lounge: VIP perks plus exclusive lounge access and traditional attire.\r\n    Platinum Navratri Experience: VIP perks plus front-row seating and a Navratri-themed gift.'),
(80, 'Christmas Wonderland', 'Goa Festival Grounds', '2024-12-25 09:00:00', '2024-12-25 23:59:00', 'Magical Christmas celebration with festive decorations, music, and joyous activities.', 2, '    Christmas Reveler: Access to the main festival grounds.\r\n    VIP Christmas Pass: VIP perks plus exclusive access to a designated VIP area.\r\n    Exclusive Christmas Lounge: VIP perks plus a guided tour of festive highlights.\r\n    Platinum Christmas Experience: VIP perks plus front-row seating and a Christmas-themed gift.'),
(81, 'Durga Puja Carnival', 'Kolkata Cultural Park', '2024-10-05 06:00:00', '2024-10-05 18:00:00', 'Grand carnival celebrating Durga Puja with cultural performances, art installations, and traditional cuisine.', 2, '    Puja Enthusiast: Access to cultural displays, art installations, and traditional cuisine.\r\n    VIP Puja Pass: VIP perks plus guided tour of the carnival exhibits.\r\n    Exclusive Puja Lounge: VIP perks plus exclusive lounge access and traditional gifts.\r\n    Platinum Puja Experience: VIP perks plus front-row seating and a personalized souvenir.'),
(82, 'Oktoberfest Celebration', 'Bangalore Beer Gardens', '2024-10-03 10:00:00', '2024-10-03 23:59:00', 'Traditional Oktoberfest celebration with live music, dance, and a wide selection of beers.', 2, '    Beer Enthusiast: Access to the main festival grounds and beer stalls.\r\n    Oktober VIP Pass: VIP perks plus exclusive access to a designated VIP area.\r\n    Exclusive Beer Lounge: VIP perks plus a guided tour of the beer varieties.\r\n    Platinum Oktober Experience: VIP perks plus front-row seating and a beer-themed gift.'),
(84, 'Tech Expo 2024', 'Bangalore Convention Center', '2024-04-10 10:00:00', '2024-04-12 23:59:00', 'Explore the latest in technology with cutting-edge gadgets, workshops, and keynote speakers.', 3, '    Expo Pass: Access to the tech expo floor and exhibits.\r\n    VIP Tech Enthusiast: VIP perks, exclusive tech demos, and early access to select exhibits.\r\n    Workshop Access: Access to workshops in addition to the main expo.\r\n    Executive VIP Pass: VIP perks plus exclusive lounge access, personalized consultations, and priority seating at keynotes.'),
(85, 'Food and Wine Festival', 'Delhi Culinary Square', '2024-06-15 10:00:00', '2024-06-18 23:59:00', 'Culinary delights and exquisite wines come together in a gastronomic celebration.', 3, '    General Admission: Access to the food stalls and general festival areas.\r\n    Wine Tasting Pass: Tastings of a selection of premium wines.\r\n    VIP Gastronome: VIP perks, exclusive tastings, and a dedicated VIP lounge.\r\n    Chef\'s Table Experience: VIP perks plus a private dining experience with a renowned chef.'),
(86, 'Fitness Expo & Marathon', 'Mumbai Sports Complex', '2024-09-01 08:00:00', '2024-09-03 23:59:00', 'Engage in fitness workshops, discover the latest fitness trends, and participate in a thrilling marathon.', 3, '    Expo Access: Access to fitness workshops, exhibits, and vendor stalls.\r\n    Marathon Registration: Entry to the marathon race and a participant\'s kit.\r\n    VIP Fitness Pass: VIP perks, exclusive fitness demos, and a dedicated lounge.\r\n    Exclusive Marathon Package: VIP perks plus personalized coaching sessions and post-marathon recovery package.'),
(87, ' Art and Craft Fair', 'Kolkata Art Gallery', '2025-01-20 12:00:00', '2025-01-22 23:59:00', 'Immerse yourself in the world of art and craft with exhibitions, workshops, and live demonstrations.', 3, '    Art Enthusiast Pass: Access to art exhibitions and general fair areas.\r\n    Craft Workshop Access: Access to hands-on craft workshops in addition to the main fair.\r\n    VIP Art Connoisseur: VIP perks, exclusive art previews, and a dedicated VIP lounge.\r\n    Masterclass Experience: VIP perks plus exclusive masterclasses with renowned artists.'),
(88, 'Science and Innovation Summit', 'Hyderabad Innovation Hub', '2024-05-20 08:00:00', '2024-05-20 23:59:00', 'Uncover the latest breakthroughs in science, technology, and innovation with keynote speakers and interactive exhibits.', 3, '    Summit Pass: Access to keynote sessions and general summit areas.\r\n    Innovation Workshop Access: Access to hands-on innovation workshops in addition to the main summit.\r\n    VIP Innovation Explorer: VIP perks, exclusive innovation demos, and a dedicated VIP lounge.\r\n    Exclusive Summit Package: VIP perks plus personalized consultations with innovators and access to exclusive breakout sessions.'),
(89, 'Fashion Extravaganza', 'Jaipur Fashion Center', '2024-08-10 10:00:00', '2024-08-12 22:00:00', 'A glamorous showcase of the latest fashion trends, runway shows, and designer exhibitions.', 3, '    Fashion Enthusiast Pass: Access to runway shows and general fashion exhibition areas.\r\n    VIP Front Row Experience: VIP perks, front-row seating, and exclusive designer previews.\r\n    Exclusive Designer Lounge: VIP perks plus access to a dedicated lounge with designers.\r\n    Fashionista VIP Package: VIP perks plus personalized consultations with fashion experts and exclusive shopping opportunities.'),
(90, 'Environmental Sustainability Symposium', 'Chennai Eco-Conference Center', '2024-10-15 10:00:00', '2024-10-17 18:00:00', 'A forum to discuss and promote environmental sustainability, featuring expert panels and eco-friendly innovations.', 3, '    Symposium Access: Access to keynote sessions and general symposium areas.\r\n    Green Innovator Pass: Access to innovation showcases and eco-friendly product demonstrations.\r\n    VIP Sustainability Advocate: VIP perks, exclusive panel discussions, and a dedicated lounge.\r\n    Eco-Leader Package: VIP perks plus exclusive consultations with environmental experts and networking opportunities.'),
(91, 'Wellness and Mindfulness Retreat', 'Rishikesh Wellness Resort', '2024-05-20 10:00:00', '2024-05-22 18:00:00', 'A rejuvenating retreat focusing on wellness, mindfulness, and holistic health practices.', 3, '    Wellness Retreat Pass: Access to wellness workshops, meditation sessions, and general retreat areas.\r\n    Mindfulness Workshop Access: Access to guided mindfulness workshops in addition to the main retreat.\r\n    VIP Serenity Package: VIP perks, exclusive wellness sessions, and a dedicated VIP relaxation area.\r\n    Exclusive Wellness Experience: VIP perks plus personalized consultations with wellness experts and exclusive wellness activities.'),
(92, 'Technology Innovation Hackathon', 'Hyderabad Innovation Hub', '2024-01-01 11:00:00', '2024-01-03 18:00:00', 'A competitive hackathon focusing on innovative solutions in technology and software development.', 3, '    Hackathon Participant: Participation in the hackathon with access to mentorship and development tools.\r\n    Tech Enthusiast Observer: Access to observe the hackathon presentations and attend panel discussions.\r\n    VIP Tech Innovator: VIP perks, exclusive tech demos, and a dedicated VIP lounge.\r\n    Exclusive Hackathon Experience: VIP perks plus personalized consultations with industry experts and exclusive access to winning team presentations.');

-- --------------------------------------------------------

--
-- Table structure for table `event_categories`
--

CREATE TABLE `event_categories` (
  `id` int(11) NOT NULL,
  `category_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `event_categories`
--

INSERT INTO `event_categories` (`id`, `category_name`, `description`) VALUES
(1, 'concerts', NULL),
(2, 'festivals', NULL),
(3, 'others', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `review_text` text NOT NULL,
  `review_date` date NOT NULL,
  `booking_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tickets`
--

CREATE TABLE `tickets` (
  `id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `ticket_type` varchar(50) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `available_tickets` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tickets`
--

INSERT INTO `tickets` (`id`, `event_id`, `ticket_type`, `price`, `available_tickets`) VALUES
(6118, 65, 'Regular', 150.00, 1200),
(6119, 65, 'VIP', 500.00, 60),
(6120, 65, 'Platinum', 1000.00, 15),
(6121, 65, 'Gold', 750.00, 24),
(6122, 66, 'Standard Pass', 250.00, 1500),
(6123, 66, 'VIP Pass', 700.00, 75),
(6124, 66, 'Exclusive', 1200.00, 30),
(6125, 66, 'Platinum Pass', 2000.00, 10),
(6126, 67, 'Jazz Enthusiast', 180.00, 800),
(6127, 67, 'Standard Jazz', 900.00, 50),
(6128, 67, 'VIP Jazz Lounge', 1200.00, 25),
(6129, 67, 'Platinum Jazz Experience', 2500.00, 10),
(6130, 68, 'Indie Insider', 2200.00, 1000),
(6131, 68, 'General Indie', 1000.00, 75),
(6132, 68, 'VIP Indie Lounge', 1500.00, 20),
(6133, 68, 'Platinum Indie Experience', 3000.00, 10),
(6134, 69, 'Maestro Pass', 2800.00, 700),
(6135, 69, 'Classical Enthusiast', 1300.00, 50),
(6136, 69, 'VIP Symphony Lounge', 2000.00, 15),
(6137, 69, 'Platinum Classical Experience', 3500.00, 10),
(6138, 70, 'General Pop Pass', 250.00, 1200),
(6139, 70, 'VIP Pop Lounge', 700.00, 40),
(6140, 70, 'Platinum Pop Experience', 1200.00, 15),
(6141, 70, 'Ultimate Pop Fan Package', 3000.00, 5),
(6142, 71, 'Standard Fusion Pass', 200.00, 800),
(6143, 71, 'VIP Fusion Lounge', 600.00, 40),
(6144, 71, 'Platinum Fusion Experience', 1000.00, 20),
(6145, 71, 'Ultimate Fusion Fan Package', 1500.00, 10),
(6146, 72, 'Country Fan Pass', 180.00, 100),
(6147, 72, 'VIP Country Lounge', 500.00, 60),
(6148, 72, 'Platinum Country Experience', 900.00, 25),
(6149, 72, 'Ultimate Country Fan Package', 1500.00, 15),
(6150, 73, 'Standard Reggae Pass', 300.00, 1500),
(6151, 73, 'VIP Reggae Lounge', 800.00, 75),
(6152, 73, 'Platinum Reggae Experience', 1200.00, 30),
(6153, 73, 'Ultimate Reggae Fan Package', 2000.00, 8),
(6154, 74, 'General Holi Pass', 100.00, 1998),
(6155, 74, 'VIP Holi Lounge', 300.00, 100),
(6156, 74, 'Platinum Holi Experience', 500.00, 30),
(6157, 74, 'Ultimate Holi Fan Package', 1000.00, 10),
(6158, 75, 'Diwali Enthusiast', 200.00, 1200),
(6159, 75, 'VIP Illumination Pass', 500.00, 60),
(6160, 75, 'Diwali VIP Lounge', 1000.00, 15),
(6161, 75, 'Platinum Diwali Experience', 1500.00, 25),
(6162, 76, 'Dandiya Dancer', 150.00, 800),
(6163, 76, 'Navratri VIP Pass', 500.00, 50),
(6164, 76, 'Exclusive Dandiya Lounge', 1000.00, 20),
(6165, 76, 'Platinum Navratri Experience', 2000.00, 10),
(6166, 77, 'Cultural Devotee', 200.00, 1000),
(6167, 77, 'Ganesh Darshan Pass', 500.00, 60),
(6168, 77, 'Exclusive Cultural Lounge', 1000.00, 25),
(6169, 77, 'Platinum Ganesh Experience', 1500.00, 15),
(6170, 78, 'Eid Shopper Pass', 150.00, 1200),
(6171, 78, 'VIP Eid Experience', 500.00, 50),
(6172, 78, 'Exclusive Shopping Lounge', 1000.00, 15),
(6173, 78, 'Platinum Eid Extravaganza', 2000.00, 10),
(6174, 79, 'Garba Enthusiast', 180.00, 1000),
(6175, 79, 'Navratri VIP Pass', 450.00, 50),
(6176, 79, 'Exclusive Garba Lounge', 900.00, 25),
(6177, 79, 'Platinum Navratri Experience', 1800.00, 15),
(6178, 80, 'Christmas Reveler', 250.00, 1200),
(6179, 80, 'VIP Christmas Pass', 600.00, 50),
(6180, 80, 'Exclusive Christmas Lounge', 1200.00, 20),
(6181, 80, 'Platinum Christmas Experience', 2000.00, 10),
(6182, 81, 'Puja Enthusiast', 200.00, 1500),
(6183, 81, 'VIP Puja Pass', 500.00, 60),
(6184, 81, 'Exclusive Puja Lounge', 1000.00, 15),
(6185, 81, 'Platinum Puja Experience', 1500.00, 25),
(6186, 82, 'Beer Enthusiast', 180.00, 1000),
(6187, 82, 'Oktober VIP Pass', 450.00, 50),
(6188, 82, 'Exclusive Beer Lounge', 900.00, 24),
(6189, 82, 'Platinum Oktober Experience', 1800.00, 15),
(6194, 84, 'Expo Pass', 300.00, 2000),
(6195, 84, 'VIP Tech Enthusiast', 800.00, 99),
(6196, 84, 'Workshop Access', 500.00, 500),
(6197, 84, 'Executive VIP Pass', 1500.00, 50),
(6198, 85, 'General Admission', 250.00, 1500),
(6199, 85, 'Wine Tasting Pass', 600.00, 200),
(6200, 85, 'VIP Gastronome', 1200.00, 75),
(6201, 85, 'Chef\'s Table Experience', 2500.00, 20),
(6202, 86, 'Expo Access', 200.00, 1000),
(6203, 86, 'Marathon Registration', 500.00, 500),
(6204, 86, 'VIP Fitness Pass', 800.00, 50),
(6205, 86, 'Exclusive Marathon Package', 1500.00, 25),
(6206, 87, 'Art Enthusiast Pass', 150.00, 1200),
(6207, 87, 'Craft Workshop Access', 300.00, 500),
(6208, 87, 'VIP Art Connoisseur', 800.00, 75),
(6209, 87, 'Masterclass Experience', 1200.00, 30),
(6210, 88, 'Summit Pass', 300.00, 1500),
(6211, 88, 'Innovation Workshop Access', 500.00, 300),
(6212, 88, 'VIP Innovation Explorer', 800.00, 50),
(6213, 88, 'Exclusive Summit Package', 1500.00, 25),
(6214, 89, 'Fashion Enthusiast Pass', 250.00, 1200),
(6215, 89, 'VIP Front Row Experience', 800.00, 100),
(6216, 89, 'Exclusive Designer Lounge', 1200.00, 50),
(6217, 89, 'Fashionista VIP Package', 2000.00, 30),
(6218, 90, 'Symposium Access', 200.00, 1000),
(6219, 90, 'Green Innovator Pass', 500.00, 150),
(6220, 90, 'VIP Sustainability Advocate', 800.00, 75),
(6221, 90, 'Eco-Leader Package', 1500.00, 40),
(6222, 91, 'Wellness Retreat Pass', 400.00, 1199),
(6223, 91, 'Mindfulness Workshop Access', 600.00, 200),
(6224, 91, 'VIP Serenity Package', 1000.00, 50),
(6225, 91, 'Exclusive Wellness Experience', 1500.00, 25),
(6226, 92, 'Hackathon Participant', 200.00, 500),
(6227, 92, 'Tech Enthusiast Observer', 100.00, 200),
(6228, 92, 'VIP Tech Innovator', 500.00, 30),
(6229, 92, 'Exclusive Hackathon Experience', 1000.00, 15),
(6238, 64, 'General', 200.00, 1000),
(6239, 64, 'VIP', 500.00, 50),
(6240, 64, 'VVIP', 1000.00, 20),
(6241, 64, 'Platinum', 1500.00, 9);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(1000) NOT NULL,
  `registeredon` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `registeredon`) VALUES
(9, 'Shodhan Rai', 'shodhan@gmail.com', 'scrypt:32768:8:1$rNRnfh9U6Xk6OTe2$9e995b16baee46ed42c3ef259a3582d660e9cf2d5d5df51dca058848e0dd53e7261962c617d334469120a84f7bd6168cc58914f5480227925f623b16762e4bf1', '2024-03-07 14:26:01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `event_id` (`event_id`),
  ADD KEY `ticket_id` (`ticket_id`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `event_categories`
--
ALTER TABLE `event_categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `event_id` (`event_id`),
  ADD KEY `fk_booking_id` (`booking_id`);

--
-- Indexes for table `tickets`
--
ALTER TABLE `tickets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tickets_ibfk_1` (`event_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=130;

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=93;

--
-- AUTO_INCREMENT for table `event_categories`
--
ALTER TABLE `event_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `tickets`
--
ALTER TABLE `tickets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6242;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  ADD CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`ticket_id`) REFERENCES `tickets` (`id`);

--
-- Constraints for table `events`
--
ALTER TABLE `events`
  ADD CONSTRAINT `events_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `event_categories` (`id`);

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `fk_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`);

--
-- Constraints for table `tickets`
--
ALTER TABLE `tickets`
  ADD CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
