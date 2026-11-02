CREATE OR REPLACE FUNCTION dw_sales_rep_by_year(
    p_schema      TEXT DEFAULT 'public',
    p_nome_view   TEXT DEFAULT 'dw_sales_rep_by_year'
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_anno_inizio INTEGER;
    v_anno_fine   INTEGER;
    v_sql       TEXT;
    v_colonne   TEXT := '';
    v_anno      INTEGER;
    v_prec      INTEGER;
    v_view      TEXT;
BEGIN
    -- Imposto dinamicamente anno inizio e anno fine
    SELECT min(year), max(year)
    INTO   v_anno_inizio, v_anno_fine
    FROM mis_dw;
    
    -- Validazione dei parametri
    IF v_anno_inizio >= v_anno_fine THEN
        RAISE EXCEPTION
            'L''anno iniziale (%) deve essere < dell''anno finale (%)',
            v_anno_inizio, v_anno_fine;
    END IF;

    -- Nome della view qualificato con lo schema
    v_view := format('%I.%I', p_schema, p_nome_view);

    -- Genera le colonne per ogni anno
    FOR v_anno IN v_anno_inizio..v_anno_fine LOOP

        -- Colonna del venduto annuale
        v_colonne := v_colonne
            || CASE WHEN v_colonne <> '' THEN ', ' ELSE '' END
            || format(
                'COALESCE(SUM(amount) FILTER (WHERE year = %s), 0.000) AS %I',
                v_anno,
                'venduto_' || v_anno
            );

        -- Dalla seconda annualità, aggiunge lo scostamento
        IF v_anno > v_anno_inizio THEN
            v_prec := v_anno - 1;

            v_colonne := v_colonne || ', ' || format(
                $fmt$
                CASE
                    WHEN COALESCE(
                        SUM(amount) FILTER (WHERE year = %s), 0
                    ) = 0
                    THEN NULL
                    ELSE ROUND(
                        (
                            COALESCE(
                                SUM(amount) FILTER (WHERE year = %s), 0
                            )
                            -
                            COALESCE(
                                SUM(amount) FILTER (WHERE year = %s), 0
                            )
                        )::numeric
                        /
                        COALESCE(
                            SUM(amount) FILTER (WHERE year = %s), 0
                        )
                        * 100,
                        2
                    )
                END AS %I
                $fmt$,
                v_prec,
                v_anno,
                v_prec,
                v_prec,
                format('%%_%s_vs_%s', v_anno, v_prec)
            );
        END IF;

    END LOOP;

    -- Costruisce la query completa
    v_sql := format(
        $sql$
        CREATE OR REPLACE VIEW %s AS
        SELECT
            sale_reps_description,
            %s,
            SUM(amount) AS totale_periodo
        FROM mis_dw
        WHERE year BETWEEN %s AND %s
        GROUP BY sale_reps_description
        $sql$,
        v_view,
        v_colonne,
        v_anno_inizio,
        v_anno_fine
    );

    -- Crea o aggiorna la view
    EXECUTE v_sql;

    RAISE NOTICE 'View % creata/aggiornata', v_view;
END;
$$;

-- creo la view dw_sales_rep_by_year
DROP VIEW IF EXISTS dw_sales_rep_by_year;
SELECT dw_sales_rep_by_year();
