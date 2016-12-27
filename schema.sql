CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    DOB VARCHAR(10),
    hometown VARCHAR(20),
    gender VARCHAR(1),
    password varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id));

CREATE TABLE Friends
  (user_id int4,
   f_id int4,
   PRIMARY KEY(user_id, f_id),
   FOREIGN KEY (user_id)
   REFERENCES Users(user_id)
   ON DELETE CASCADE
   );

CREATE TABLE Albums
  (Album_id int4 AUTO_INCREMENT,
   user_id int4 NOT NULL,
   name VARCHAR(255) NOT NULL,
   date_of_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (Album_id),
   FOREIGN KEY(user_id)
   REFERENCES Users(user_id)
   ON DELETE CASCADE,
   CONSTRAINT uc_name UNIQUE (user_id,name));

CREATE TABLE Photos
(
  photo_id int4 AUTO_INCREMENT,
  Album_id int4,
  imgdata longblob,
  caption VARCHAR(255),
  INDEX upid_idx (Album_id),
  CONSTRAINT photo_pk PRIMARY KEY (photo_id),
  FOREIGN KEY (Album_id)
  REFERENCES Albums(Album_id)
  ON DELETE CASCADE
);

CREATE TABLE Comments
  (Comment_id int4 AUTO_INCREMENT,
   text1 VARCHAR(255),
   dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   Photo_id int4,
   FOREIGN KEY(Photo_id)
   REFERENCES Photos(Photo_id)
   ON DELETE CASCADE,
   PRIMARY KEY (Comment_id));

CREATE TABLE Tags
  (description VARCHAR(255) NOT NULL,
   CHECK (desciprtion NOT LIKE '% %'),
   CHECK (lower(description) = description),
   PRIMARY KEY(description)
  );

CREATE TABLE taged_by
 (Photo_id int4,
  description VARCHAR(255) NOT NULL,
  FOREIGN KEY(Photo_id)
  REFERENCES Photos(Photo_id)
  ON DELETE CASCADE,
  FOREIGN KEY(description)
  REFERENCES Tags(description),
  CONSTRAINT uc_tag UNIQUE (Photo_id,description));

 CREATE TABLE likes
   (user_id int4,
    Photo_id int4,
    FOREIGN KEY(user_id)
    REFERENCES Users(User_id)
    ON DELETE CASCADE,
    FOREIGN KEY(Photo_id)
    REFERENCES Photos(photo_id)
    ON DELETE CASCADE,
    PRIMARY KEY (user_id, Photo_id));

CREATE TABLE leaves
   (user_id int4, 
    Comment_id int4,
    FOREIGN KEY(Comment_id)
    REFERENCES Comments(Comment_id)
    ON DELETE CASCADE,
    PRIMARY KEY (user_id, Comment_id));

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('wei0496@bu.edu', 'test');
