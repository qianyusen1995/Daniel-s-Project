USE `movie`;
ALTER TABLE `comment` AUTO_INCREMENT=1;
INSERT INTO `comment`(`content`,movie_id,user_id,`addtime`) VALUES ('好看',1,2,NOW());