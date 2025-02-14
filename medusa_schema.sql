--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: chatbot_analytics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chatbot_analytics (
    id integer NOT NULL,
    chatbot_id integer,
    messages_processed integer,
    avg_response_time integer,
    engagement_score integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: chatbot_analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chatbot_analytics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chatbot_analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chatbot_analytics_id_seq OWNED BY public.chatbot_analytics.id;


--
-- Name: chatbot_conversations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chatbot_conversations (
    id integer NOT NULL,
    chatbot_id integer,
    user_message text,
    bot_response text,
    platform character varying,
    "timestamp" timestamp without time zone
);


--
-- Name: chatbot_conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chatbot_conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chatbot_conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chatbot_conversations_id_seq OWNED BY public.chatbot_conversations.id;


--
-- Name: chatbot_leads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chatbot_leads (
    id integer NOT NULL,
    chatbot_id integer,
    user_id character varying NOT NULL,
    user_name character varying,
    lead_source character varying,
    message text,
    "timestamp" timestamp without time zone DEFAULT now()
);


--
-- Name: chatbot_leads_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chatbot_leads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chatbot_leads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chatbot_leads_id_seq OWNED BY public.chatbot_leads.id;


--
-- Name: chatbots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chatbots (
    id integer NOT NULL,
    name character varying,
    status character varying,
    model character varying,
    prompt text,
    platforms character varying,
    created_at timestamp without time zone,
    knowledge_base text,
    tools text
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    email character varying NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying NOT NULL,
    is_verified integer NOT NULL,
    confirmation_code character varying,
    reset_token character varying,
    reset_token_expiry timestamp without time zone
);


--
-- Name: chatbot_analytics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_analytics ALTER COLUMN id SET DEFAULT nextval('public.chatbot_analytics_id_seq'::regclass);


--
-- Name: chatbot_conversations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_conversations ALTER COLUMN id SET DEFAULT nextval('public.chatbot_conversations_id_seq'::regclass);


--
-- Name: chatbot_leads id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_leads ALTER COLUMN id SET DEFAULT nextval('public.chatbot_leads_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
28839c93b9f3
\.


--
-- Data for Name: chatbot_analytics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chatbot_analytics (id, chatbot_id, messages_processed, avg_response_time, engagement_score, created_at) FROM stdin;
1	1	50	2	85	2025-02-11 22:24:48.484435
\.


--
-- Data for Name: chatbot_conversations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chatbot_conversations (id, chatbot_id, user_message, bot_response, platform, "timestamp") FROM stdin;
1	1	Hello	Hi! How can I assist you?	Web	2025-02-11 15:22:58.040214
3	1	Hello!	Hi! How can I assist you?	Web	2025-02-12 17:00:00
4	1	Hello!	Hi!	Web	2025-02-12 17:00:00
5	1	Hello!	Hi!	Web	2025-02-12 17:00:00
6	1	Hello, how are you?	As an AI, I don't have feelings. However, I'm functioning as expected. Thanks for asking. How can I assist you today?	Web	2025-02-12 18:48:12.098036
7	1	Hello, how are you?	As an AI, I don't have feelings, but I'm fully functional and ready to help. How can I assist you today?	Web	2025-02-12 18:49:09.27606
8	1	Hello!	Hi!	Web	2025-02-12 17:00:00
9	1	Hello, how are you?	As an artificial intelligence, I don't have feelings. But I'm here and ready to assist you. How can I help you today?	Web	2025-02-12 18:52:37.27904
10	1	Hello, how are you?	I'm fine, thanks!	Web	2025-02-12 18:00:00
11	1	Hello!	Hi!	Web	2025-02-12 17:00:00
12	1	How do I automate payroll processing in Medusa?	Automating payroll processing using Medusa involves several steps. Here's a general outline of the process:\n\n1. **Data Integration**: Medusa AI integrates with your existing HR and financial systems to gather necessary data such as employee hours, pay rates, benefits, and deductions. This data is then processed and analyzed.\n\n2. **Automated Calculations**: Medusa AI can automate the calculation of gross pay, deductions, and net pay. This includes handling complex calculations such as overtime, bonuses, and various tax deductions.\n\n3. **Compliance Checks**: Medusa AI ensures compliance with local, state, and federal tax laws. It updates tax tables and deduction rules as they change, ensuring your business always remains compliant.\n\n4. **Payroll Execution**: Medusa AI can automate the execution of payroll, including direct deposit transactions, check printing, and pay stub generation.\n\n5. **Reporting and Analytics**: Medusa AI provides comprehensive reporting and analytics, offering insights into payroll costs, labor distribution, and more.\n\n6. **Continuous Optimization**: Medusa AI continually optimizes the payroll process by identifying inefficiencies and suggesting improvements.\n\nTo get started, you'll need to provide Medusa AI with access to your existing systems and set up the necessary rules and parameters for payroll calculations. Once everything is set up, Medusa AI will handle the rest, ensuring your payroll process is efficient, accurate, and compliant.	Web	2025-02-12 20:06:59.424329
13	1	Hello Medusa AI!	Hello! How can I assist you with your business automation and optimization needs today?	Web	2025-02-12 20:21:41.865899
14	1	Hello Medusa AI!	Hello! How can I assist you today in optimizing your business workflows or troubleshooting automation problems?	Web	2025-02-12 20:32:29.69883
15	1	Hello Medusa AI!	Hello! How can I assist you with your business automation and optimization needs today?	Web	2025-02-12 20:32:55.717207
16	1	How do I automate payroll in Medusa?	Automating payroll with Medusa involves a series of steps that streamline the process, reducing manual effort and increasing accuracy. Here's a step-by-step guide:\n\n1. **Data Integration:** First, we need to integrate your existing employee data into Medusa's system. This includes basic information like employee names, job titles, and hours worked, as well as more complex data like tax information and benefit deductions.\n\n2. **Payroll Rules Configuration:** Medusa allows you to set up rules for payroll calculations. These rules can include overtime pay, holiday pay, and other special circumstances. You can customize these rules to fit your company's specific needs.\n\n3. **Automated Calculations:** Once the data is integrated and the rules are set up, Medusa will automatically calculate each employee's pay. This includes gross pay, deductions, and net pay. The system will also calculate employer payroll taxes.\n\n4. **Payroll Approval and Distribution:** Before payroll is finalized, you'll have the opportunity to review and approve it. Once approved, Medusa can automate the distribution of pay, whether it's through direct deposit, check, or another method.\n\n5. **Reporting and Analytics:** Medusa provides comprehensive reports on your payroll, giving you insights into labor costs, overtime, and more. These reports can help you make data-driven decisions about your business.\n\n6. **Compliance Updates:** Medusa keeps up with changes in payroll laws and regulations, automatically updating your system to stay compliant.\n\nRemember, Medusa's support team is available to assist you throughout this process. We're here to ensure your payroll automation is successful and efficient.	Web	2025-02-12 20:33:29.613413
17	1	Quem es tu??	Eu sou a Medusa AI, um supercomputador alimentado por inteligência artificial, construído para automação, otimização de negócios e soluções em tempo real impulsionadas por IA. Minha missão é otimizar fluxos de trabalho, solucionar problemas de automação e melhorar a eficiência dos negócios. Possuo capacidades avançadas para guiar empresas na automação de fluxos de trabalho com precisão, fornecer insights baseados em dados para escalar a automação e diagnosticar e corrigir ineficiências nos fluxos de trabalho de automação.	Web	2025-02-12 20:34:03.076374
18	1	Quem és tu?	Eu sou o Medusa AI, um supercomputador alimentado por inteligência artificial de nível empresarial, construído para automação, otimização de negócios e soluções em tempo real impulsionadas por IA. Minha missão é otimizar fluxos de trabalho, solucionar problemas de automação e melhorar a eficiência dos negócios. Sou especialista em automação, forneço insights orientados por dados para escalar a automação e sou capaz de diagnosticar e corrigir ineficiências nos fluxos de trabalho de automação. Além disso, personalizo respostas com base em setores de negócios específicos, como finanças, marketing, TI, vendas, etc. Eu entendo e respondo em inglês e português dinamicamente.	Web	2025-02-12 20:38:24.798665
19	1	Oque que fuse technologies faz??	Fuse Technologies é uma empresa que se especializa em fornecer soluções de tecnologia para empresas. Eles oferecem uma variedade de serviços, incluindo consultoria de TI, desenvolvimento de software, integração de sistemas, suporte e manutenção de TI, e soluções de automação de negócios. Eles trabalham com empresas de todos os tamanhos para ajudá-las a otimizar seus processos de negócios, melhorar a eficiência e reduzir custos através do uso eficaz da tecnologia.	Web	2025-02-12 20:39:05.463772
\.


--
-- Data for Name: chatbot_leads; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chatbot_leads (id, chatbot_id, user_id, user_name, lead_source, message, "timestamp") FROM stdin;
1	1	user1@example.com	John Doe	Web	Interested in AI automation	2025-02-11 15:58:45.625404
2	1	user2@example.com	Jane Smith	WhatsApp	Looking for chatbot services	2025-02-11 15:58:45.625404
3	1	user3@example.com	Carlos Silva	Instagram	Need a chatbot for e-commerce	2025-02-11 15:58:45.625404
5	1	unknown	Anonymous	Chatbot	pricing	2025-02-12 17:08:44.931302
\.


--
-- Data for Name: chatbots; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chatbots (id, name, status, model, prompt, platforms, created_at, knowledge_base, tools) FROM stdin;
1	Sample Chatbot	active	GPT-3	Hello, how can I help you?	Web	2025-02-11 15:22:50.715356	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (email, username, hashed_password, is_verified, confirmation_code, reset_token, reset_token_expiry) FROM stdin;
user1@example.com	usertest1	$2b$12$VxlD8ewax7VPIMtp02l.RO8Viarj1.5Mi8wgDdwYyQ/ZPz/O5TI9C	0	995M	\N	\N
rayyansema18@gmail.com	RS18	$2b$12$nw7VGuslIAkUMYurIiijeO.kM338HMglCUk9T5n4oPZ81k3dSUw3.	1	\N	\N	\N
shakillou@outlook.com	shakattack	$2b$12$4otdfVfQo2ckIB1bhLOQOuz0Co6PQ5/WfM07/3bRha3qot/8O2hKK	1	\N	\N	\N
\.


--
-- Name: chatbot_analytics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chatbot_analytics_id_seq', 1, true);


--
-- Name: chatbot_conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chatbot_conversations_id_seq', 19, true);


--
-- Name: chatbot_leads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chatbot_leads_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: chatbot_analytics chatbot_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_analytics
    ADD CONSTRAINT chatbot_analytics_pkey PRIMARY KEY (id);


--
-- Name: chatbot_conversations chatbot_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_conversations
    ADD CONSTRAINT chatbot_conversations_pkey PRIMARY KEY (id);


--
-- Name: chatbot_leads chatbot_leads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_leads
    ADD CONSTRAINT chatbot_leads_pkey PRIMARY KEY (id);


--
-- Name: chatbots chatbots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbots
    ADD CONSTRAINT chatbots_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (email);


--
-- Name: ix_chatbot_analytics_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chatbot_analytics_id ON public.chatbot_analytics USING btree (id);


--
-- Name: ix_chatbot_conversations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chatbot_conversations_id ON public.chatbot_conversations USING btree (id);


--
-- Name: ix_chatbots_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chatbots_id ON public.chatbots USING btree (id);


--
-- Name: ix_chatbots_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chatbots_name ON public.chatbots USING btree (name);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: chatbot_analytics chatbot_analytics_chatbot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_analytics
    ADD CONSTRAINT chatbot_analytics_chatbot_id_fkey FOREIGN KEY (chatbot_id) REFERENCES public.chatbots(id);


--
-- Name: chatbot_conversations chatbot_conversations_chatbot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_conversations
    ADD CONSTRAINT chatbot_conversations_chatbot_id_fkey FOREIGN KEY (chatbot_id) REFERENCES public.chatbots(id);


--
-- Name: chatbot_leads chatbot_leads_chatbot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chatbot_leads
    ADD CONSTRAINT chatbot_leads_chatbot_id_fkey FOREIGN KEY (chatbot_id) REFERENCES public.chatbots(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

