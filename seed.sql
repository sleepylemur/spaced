drop table if exists questions cascade;
create table questions (
  id serial primary key,
  question text,
  answer text
);

drop table if exists history cascade;
create table history (
  id serial primary key,
  correct bool,
  question_id int,

  constraint fk_question_id foreign key(question_id)
    references questions(id)
    on delete cascade
    on update cascade
);

insert into questions (question,answer) values
('a?','no'),
('b?','yes');

