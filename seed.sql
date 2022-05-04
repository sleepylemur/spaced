CREATE TYPE question_status AS ENUM ('unknown', 'learning', 'known');

drop table if exists questions cascade;
create table questions (
  id serial primary key,
  question text,
  answer text,
  status question_status
);

drop table if exists users cascade;
create table users (
  id serial primary key,
  email text,
  password text
);

drop table if exists history cascade;
create table history (
  id serial primary key,
  correct bool,
  question_id int,
  ts timestamp,

  constraint fk_question_id foreign key(question_id)
    references questions(id)
    on delete cascade
    on update cascade
);

insert into questions (question, answer, status) values
('a?','no','unknown'),
('b?','yes','unknown'),
('c?','yes','unknown'),
('d?','yes','unknown'),
('e?','yes','unknown');

-- insert into history (question_id, correct) values
-- (1, true),
-- (4, false),
-- (3, false),
-- (1, true),
-- (2, true),
-- (1, true);