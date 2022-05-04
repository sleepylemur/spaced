drop table if exists users cascade;
create table users (
  id serial primary key,
  email text,
  password text
);

create TYPE question_status as enum ('unknown', 'learning', 'known');

drop table if exists questions cascade;
create table questions (
  id serial primary key,
  question text not null,
  answer text not null,
  status question_status not null default 'unknown',
  user_id int not null,

  constraint fk_questions_user_id foreign key(user_id)
    references users(id)
    on delete cascade
    on update cascade
);

drop table if exists history cascade;
create table history (
  id serial primary key,
  correct bool not null,
  question_id int not null,
  user_id int not null,
  ts timestamp not null default current_timestamp,

  constraint fk_history_question_id foreign key(question_id)
    references questions(id)
    on delete cascade
    on update cascade,

  constraint fk_history_user_id foreign key(user_id)
    references users(id)
    on delete cascade
    on update cascade
);

insert into users (id, email, password) values
(1,'a@a.com','pbkdf2:sha256:260000$GsJFyKjWWdDEg919$35d3f2e9e27584e627a310e47c1f547f29ebcee977011d83c597e26e04b6e836');

insert into questions (question, answer, status, user_id) values
('a?','no','unknown',1),
('b?','yes','unknown',1),
('c?','yes','unknown',1),
('d?','yes','unknown',1),
('e?','yes','unknown',1);

-- insert into history (question_id, correct) values
-- (1, true),
-- (4, false),
-- (3, false),
-- (1, true),
-- (2, true),
-- (1, true);