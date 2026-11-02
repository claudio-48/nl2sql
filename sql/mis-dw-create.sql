begin;

-- Time dimension table. 
create table time_dimension (
    time_key                integer primary key,
    full_date               date    not null,
    year_and_month          integer not null,
    year_and_month_date     date    not null,  -- first month's day
    year		    integer not null,
    month                   integer not null,  -- 1 to 12
    alpha_month		    varchar(9) not null,
    alpha_month_short       char(3) not null,
    year_and_quarter        integer not null,
    alpha_quarter           char(6) not null
);

create index time_dimension_idx1 on time_dimension (year_and_month);
create index time_dimension_idx2 on time_dimension (year);
create index time_dimension_idx3 on time_dimension (month);
create index time_dimension_idx4 on time_dimension (alpha_month);
create index time_dimension_idx5 on time_dimension (alpha_month_short);
create index time_dimension_idx6 on time_dimension (year_and_quarter);
create index time_dimension_idx7 on time_dimension (alpha_quarter);
create index time_dimension_idx8 on time_dimension (full_date);
create index time_dimension_idx9 on time_dimension (year_and_month_date);

comment on column time_dimension.year_and_month is 'YYYYMM di full_date. Ad es. 202003 per Marzo 2020';
comment on column time_dimension.year_and_month_date is 'YYYYMMDD primo giorno del mese di full_date. Ad es. 20200301 per full_date 20200319';
comment on column time_dimension.year is 'YYYY di full_date.';
comment on column time_dimension.month is 'MM di full_date.';
comment on column time_dimension.alpha_month is 'Mese di full_date in chiaro. Uno dei seguenti; Gennaio, Febbraio, Marzo, Aprile, Maggio, Giugno, Luglio, Agosto, Settembre, Ottobre, Novembre, Dicembre';
comment on column time_dimension.alpha_month_short is 'Mese di full_date abbreviato a tre lettere. Uno dei seguenti: GEN, FEB, MAR, APR, MAG, GIU, LUG, AGO, SET, OTT, NOV, DIC';
comment on column time_dimension.year_and_quarter is 'Anno e trimestre di full_date. Ad es. 20201 per primo trimestre 2020';
comment on column time_dimension.alpha_quarter is 'Trimestre di full_date nel formato nTrim. Uno dei seguenti: 1Trim, 2Trim, 3Trim, 4Trim';

-- Product dimension table. 

create table product_dimension (
    product_key             integer primary key
   ,product_code            varchar(40)
   ,product_description     varchar(1000)
   ,category_code           varchar(20)
   ,category_description    varchar(1000)
);

create index product_dimension_idx1 on product_dimension (product_code);
create index product_dimension_idx2 on product_dimension (category_code);

comment on column product_dimension.category_code is 'Codice della categoria merceologica';
comment on column product_dimension.category_description is 'Descrizione della categoria merceologica';

-- Customer dimension table. 

create table customer_dimension (
    customer_key            integer primary key
   ,customer_code           varchar(40)
   ,customer_description    varchar(1000)
   ,customer_type           varchar(50)
);

create index customer_dimension_idx1 on customer_dimension (customer_code);
create index customer_dimension_idx2 on customer_dimension (customer_type);

comment on column customer_dimension.customer_code is 'Codice Cliente';
comment on column customer_dimension.customer_type is 'Tipo Cliente';

-- Sale zones dimension

create table sale_zones_dimension (
    sale_zones_key            integer primary key
   ,sale_zones_code           varchar(40)
   ,sale_zones_description    varchar(1000)
);

create index sale_zones_dimension_idx1 on sale_zones_dimension (sale_zones_code);

comment on column sale_zones_dimension.sale_zones_code is 'Codize zona di vendita';

-- Sale reps dimension table. 

create table sale_reps_dimension (
    sale_reps_key            integer primary key
   ,sale_reps_code           varchar(40)
   ,sale_reps_description    varchar(1000)
);

create index sale_reps_dimension_idx1 on sale_reps_dimension (sale_reps_code);

comment on column sale_reps_dimension.sale_reps_code is 'Codize rappresentante';

--
--  The 'facts' table is based on order lines
--

create table order_lines_dw (
  line_id            integer primary key         -- same key as mis_order_lines
  -- the dimensions
 ,time_key           integer not null references time_dimension
 ,customer_key       integer not null references customer_dimension
 ,product_key        integer not null references product_dimension
 ,sale_zones_key     integer not null references sale_zones_dimension
 ,sale_reps_key      integer not null references sale_reps_dimension
  -- the facts
 ,quantity           numeric(14,2)
 ,amount             numeric(12,3)
  );

comment on column order_lines_dw.quantity is 'Quantità ordinata';
comment on column order_lines_dw.amount is 'Importo netto della riga d''ordine, in valuta locale, IVA esclusa';

-- generic data view

create view mis_dw as
  select 
    l.quantity, l.amount,
    -- ah_edit_num(l.quantity, 2) as quantity_pretty,
    -- ah_edit_num(l.amount, 2) as amount_pretty,
    p.product_code, p.product_description, p.category_code, p.category_description,
    c.customer_code, c.customer_description, c.customer_type,
    t.full_date as order_date, t.year, t.year_and_month, t.year_and_month_date, t.month,
    t.alpha_month, t.alpha_month_short, t.year_and_quarter, t.alpha_quarter,
    s.sale_reps_code, s.sale_reps_description,
    z.sale_zones_code, z.sale_zones_description
  from order_lines_dw l
       join sale_zones_dimension z on l.sale_zones_key = z.sale_zones_key
       join sale_reps_dimension  s on l.sale_reps_key  = s.sale_reps_key
       join time_dimension t       on l.time_key       = t.time_key
       join product_dimension p    on l.product_key    = p.product_key 
       join customer_dimension c   on l.customer_key   = c.customer_key;



end;
