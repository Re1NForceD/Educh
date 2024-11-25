DROP DATABASE IF EXISTS educh_db;
CREATE DATABASE IF NOT EXISTS educh_db DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
use educh_db;

CREATE TABLE IF NOT EXISTS course
(
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(64)  NOT NULL,
  hash       VARCHAR(255) NOT NULL,
  channel_id VARCHAR(64)  NULL     DEFAULT null,
  started_at TIMESTAMP    NULL     DEFAULT null,
  created_at TIMESTAMP    not null default CURRENT_TIMESTAMP
);

create table if not exists event_type
(
  id   int unsigned not null auto_increment primary key,
  name varchar(10) not null
);

insert ignore into event_type (id, name)
values
(1, 'resources'),
(2, 'class'),
(3, 'test'),
(4, 'assignment');

create table if not exists course_event
(
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  course_id     int unsigned not null,
  event_type_id int unsigned not null,
  name          varchar(255) not null,
  start_time    TIMESTAMP    not null,
  info          text         not null,
  
  published  BOOL      not null default 0,
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  edited_at  TIMESTAMP not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  constraint course_event_course_id_cnstr foreign key(course_id) references course(id),
  constraint course_event_event_type_id_cnstr foreign key(event_type_id) references event_type(id)
);

create table if not exists course_event_details_resources
(
  event_id   INT UNSIGNED NOT NULL PRIMARY KEY,
  
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  edited_at  TIMESTAMP not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  constraint resources_details_event_id_cnstr foreign key(event_id) references course_event(id)
);

create table if not exists course_event_details_class
(
  event_id   INT UNSIGNED NOT NULL PRIMARY KEY,
  duration_m int unsigned not null,
  url        text         not null,
  
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  edited_at  TIMESTAMP not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  constraint class_details_event_id_cnstr foreign key(event_id) references course_event(id)
);

create table if not exists course_event_details_test
(
  event_id   INT UNSIGNED NOT NULL PRIMARY KEY,
  duration_m int unsigned not null,
  configs    json         not null,
  
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  edited_at  TIMESTAMP not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  constraint test_details_event_id_cnstr foreign key(event_id) references course_event(id)
);

create table if not exists course_event_details_assignment
(
  event_id   INT UNSIGNED NOT NULL PRIMARY KEY,
  
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  edited_at  TIMESTAMP not null default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  constraint assignment_details_event_id_cnstr foreign key(event_id) references course_event(id)
);

create table if not exists user_role
(
  id   int unsigned not null auto_increment primary key,
  name varchar(10) not null
);

insert ignore into user_role (id, name)
values
(1, 'guest'),
(2, 'learner'),
(3, 'teacher'),
(4, 'master');

create table if not exists course_user
(
  course_id   int unsigned not null,
  platform_id VARCHAR(64)  NOT NULL,
  name        VARCHAR(64)  not null,
  role_id     int unsigned not null,
  created_at  TIMESTAMP not null default CURRENT_TIMESTAMP,
  
  primary key(course_id, platform_id),
  index (platform_id),
  constraint course_user_course_id_cnstr foreign key(course_id) references course(id),
  constraint course_user_role_id_cnstr foreign key(role_id) references user_role(id) 
);

create table if not exists course_event_submission
(
  id         int unsigned not null auto_increment primary key,
  event_id   INT UNSIGNED NOT NULL,
  user_id    VARCHAR(64)  NOT NULL,
  submission  text        not null,
  submitter_id VARCHAR(64)    null,
  result     int unsigned     null,
  
  created_at TIMESTAMP not null default CURRENT_TIMESTAMP,
  
  constraint ce_submission_event_id_cnstr foreign key(event_id) references course_event(id)
);

-- test lines
insert ignore into course (id, name, hash, channel_id) -- , started_at)
values
(1, 'test_course', '$2b$12$PktaStHWQuZB70nfWirm3ObSVY783bdnK5/WOpkrICCxv3H3m.7k6', 'C07TAH28YUC'); -- , '2024-10-11');

insert ignore into course_user (course_id, platform_id, name, role_id)
values
(1, 'U07MAGQ4PU2', 'Bohdan Vasylenko', 4),
(1, 'U07NVTE0UJD', 'Bohdan Learner', 1);

-- insert ignore into course_event (course_id, event_type_id, start_time, duration_m)
-- values
-- (1, 1, TIMESTAMPADD(day, 1, CURRENT_TIMESTAMP()), null),
-- (1, 2, TIMESTAMPADD(day, 2, CURRENT_TIMESTAMP()), null),
-- (1, 3, TIMESTAMPADD(day, 3, CURRENT_TIMESTAMP()), 90),
-- (1, 4, TIMESTAMPADD(day, 4, CURRENT_TIMESTAMP()), 20);

-- show processlist;
-- SELECT * FROM performance_schema.processlist
-- select u.id, u.platform_id, u.name, cu.role_id from course_user cu join user u on u.id = cu.user_id where cu.course_id = 1;

-- select ce.id, ce.event_type_id, ce.name, ce.start_time, cerd.info, cecd.duration_m, cetd.duration_m 
-- from course_event ce
-- left outer join course_event_resources_details cerd on ce.event_data_id = cerd.id
-- left outer join course_event_class_details cecd on ce.event_data_id = cecd.id
-- left outer join course_event_test_details cetd on ce.event_data_id = cetd.id
-- where course_id = 1;
