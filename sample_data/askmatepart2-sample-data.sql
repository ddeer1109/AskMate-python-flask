ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;

-- ==============================================================================
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS pk_users_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_statistics DROP CONSTRAINT IF EXISTS pk_users_statistics_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS pk_users_activity_id CASCADE;


ALTER TABLE IF EXISTS ONLY public.users_statistics DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS fk_users_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS fk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users_activity DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;


DROP TABLE IF EXISTS public.users;
CREATE TABLE users (
    id serial NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    registration_date timestamp without time zone
);


DROP TABLE IF EXISTS public.users_activity;
CREATE TABLE users_activity (
    id serial NOT NULL,
    user_id integer NOT NULL,
    question_id integer,
    answer_id integer,
    comment_id integer,
    tag_id integer
);


DROP TABLE IF EXISTS public.users_statistics;
CREATE TABLE users_statistics(
    id serial NOT NULL,
    user_id integer NOT NULL,
    question_count integer,
    answer_count integer,
    comment_count integer,
    reputation_value integer
);


DROP TABLE IF EXISTS public.users_votes;
CREATE TABLE users_votes(
    user_id integer NOT NULL,
    question_id integer,
    answer_id integer,
    vote_value integer
);



-- ==============================================================================
DROP TABLE IF EXISTS public.question;
CREATE TABLE question (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    title text,
    message text,
    image text
);


DROP TABLE IF EXISTS public.answer;
CREATE TABLE answer (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    vote_number integer,
    question_id integer,
    message text,
    image text
);


DROP TABLE IF EXISTS public.comment;
CREATE TABLE comment (
    id serial NOT NULL,
    question_id integer,
    answer_id integer,
    message text,
    submission_time timestamp without time zone,
    edited_count integer
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);

ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);



-- ==============================================
ALTER TABLE ONLY users_statistics
    ADD CONSTRAINT pk_users_statistics_id PRIMARY KEY(id);

ALTER TABLE ONLY users_activity
    ADD CONSTRAINT pk_users_activity_id PRIMARY KEY(id);

ALTER TABLE ONLY users
    ADD CONSTRAINT pk_users_id PRIMARY KEY (id);


ALTER TABLE ONLY users_activity
    ADD CONSTRAINT fk_users_id FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY users_activity
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY users_activity
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);

ALTER TABLE ONLY users_activity
    ADD CONSTRAINT fk_comment_id FOREIGN KEY (comment_id) REFERENCES comment(id);

ALTER TABLE ONLY users_activity
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);

ALTER TABLE ONLY users_statistics
    ADD CONSTRAINT fk_users_id FOREIGN KEY (user_id) REFERENCES users(id);

-- ==============================================





INSERT INTO question VALUES (0, '2017-04-28 08:29:00', 29, 7, 'How to make lists in Python?', 'I am totally new to this, any hints?', 'none.jpg');
INSERT INTO question VALUES (1, '2017-04-29 09:19:00', 15, 9, 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 'none.jpg');
INSERT INTO question VALUES (2, '2017-05-01 2:41:00', 1364, 57, 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.
', 'none.jpg');
SELECT pg_catalog.setval('question_id_seq', 2, true);
INSERT INTO answer VALUES (1, '2017-04-28 16:49:00', 4, 1, 'You need to use brackets: my_list = []', 'none.jpg');
INSERT INTO answer VALUES (2, '2017-04-25 14:42:00', 35, 1, 'Look it up in the Python docs', 'none.jpg');
SELECT pg_catalog.setval('answer_id_seq', 2, true);

INSERT INTO comment VALUES (1, 0, NULL, 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment VALUES (2, NULL, 1, 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');
SELECT pg_catalog.setval('comment_id_seq', 2, true);

INSERT INTO tag VALUES (1, 'python');
INSERT INTO tag VALUES (2, 'sql');
INSERT INTO tag VALUES (3, 'css');
SELECT pg_catalog.setval('tag_id_seq', 3, true);

INSERT INTO question_tag VALUES (0, 1);
INSERT INTO question_tag VALUES (1, 3);
INSERT INTO question_tag VALUES (2, 3);

-- ===========================================================================
INSERT INTO users VALUES (1, 'user1', '$2b$12$KNDJjCLYKvTNJzfUzaGmPujpwEHCHVASvWLvhUACDiWqW9wMHDs1C', '2020-05-01 05:49:00');
INSERT INTO users VALUES (2, 'user2', '$2b$12$KNDJjCLYKvTNJzfUzaGmPujpwEHCHVASvWLvhUACDiWqW9wMHDs1C', '2020-06-01 05:49:00');
SELECT pg_catalog.setval('users_id_seq', 3, true);

INSERT INTO users_activity VALUES (1, 1, 1, null, null, null);
INSERT INTO users_activity VALUES (2, 1, 2, null, null, null);

INSERT INTO users_activity VALUES (3, 1, null, 1, null, null);
INSERT INTO users_activity VALUES (4, 1, null, 2, null, null);

INSERT INTO users_activity VALUES (5, 1, null, null, 1, null);
INSERT INTO users_activity VALUES (6, 1, null, null, 2, null);

INSERT INTO users_statistics VALUES (1, 1, 1, 1, 1, 6);
INSERT INTO users_statistics VALUES (2, 2, 2, 2, 2, 4);
SELECT pg_catalog.setval('users_statistics_id_seq', 3, true);
