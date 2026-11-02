--begin;

-- populate the time_dimension table
CREATE OR REPLACE FUNCTION populate_time_dimension(
    p_start_date date    DEFAULT DATE '2014-01-01',
    p_days       integer DEFAULT 6000
) RETURNS integer AS $$
DECLARE
    alpha_months   text[] := ARRAY['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno',
                                   'Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre'];
    short_months   text[] := ARRAY['GEN','FEB','MAR','APR','MAG','GIU',
                                   'LUG','AGO','SET','OTT','NOV','DIC'];
    alpha_quarters text[] := ARRAY['1Trim','2Trim','3Trim','4Trim'];
    d date;
    m integer;
    q integer;
BEGIN
    FOR i IN 1..p_days LOOP
        d := p_start_date;
        m := EXTRACT(month   FROM d)::integer;
        q := EXTRACT(quarter FROM d)::integer;

        INSERT INTO time_dimension (
            time_key, full_date, year_and_month,
	    year_and_month_date, year, month,
            alpha_month, alpha_month_short, year_and_quarter, alpha_quarter
        ) VALUES (
            i,
	    d,
            to_char(d, 'YYYYMM')::integer,
            date_trunc('month', d),
            to_char(d, 'YYYY')::integer,	    
            to_char(d, 'MM')::integer,
            alpha_months[m],
            short_months[m],
	    -- poiché il quarter è necessariamente di una cifra uso l'aritmetica per concatenare i valori
	    to_char(d, 'YYYY')::integer * 10 + q,
            alpha_quarters[q]
        );

        p_start_date := p_start_date + interval '1 day';
	
    END LOOP;

    RETURN p_days;
END;
$$ LANGUAGE plpgsql;

SELECT populate_time_dimension(); 

-- populate the product_dimension table
insert into product_dimension (
    select p.product_id
          ,p.product_code
          ,p.upper_title
          ,c.product_category_code
          ,c.product_category_description
    from mis_fast_products p, mis_product_categories c 
    where p.category_id = c.product_category_id
);

-- populate the customer_dimension table
insert into customer_dimension (
    select c.party_id
          ,c.party_code
          ,c.title
          ,t.party_type_description as customer_type
    from mis_customers c, mis_party_types t
    where c.party_type_id = t.party_type_id
);

-- populate the sale_zones_dimension table
insert into sale_zones_dimension (
    select z.zone_id
          ,z.zone_code
          ,z.zone_description
    from mis_sale_zones z
);

-- populate the sale_reps_dimension table
insert into sale_reps_dimension (
    select s.sale_rep_id
          ,s.sale_rep_code
          ,s.sale_rep_description
    from mis_sale_reps s
);

-- populate the facts table
insert into order_lines_dw (
    select l.line_id
          ,(select t.time_key 
            from time_dimension t 
            where o.order_date = t.full_date)
          ,o.customer_id
          ,l.product_id
          ,o.zone_id
          ,o.sale_rep_id
          ,l.qty_ordered
          ,l.line_price
    from mis_fast_order_lines l
    join mis_orders           o on l.order_id = o.order_id
    join sale_zones_dimension z on z.sale_zones_key = o.zone_id
    join sale_reps_dimension  s on s.sale_reps_key  = o.sale_rep_id
    where o.is_approved_p = 't'
      and o.order_date >= '2014-01-01'::date 
);


--end;
