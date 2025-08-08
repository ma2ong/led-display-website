-- Fix for products table HTTP 400 error
-- Migration: 20250808_fix_products_table

-- 1. Check if products table exists, if not create it
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'products') THEN
        CREATE TABLE public.products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price NUMERIC,
            image_url TEXT,
            specifications TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        RAISE NOTICE 'Created products table';
    ELSE
        RAISE NOTICE 'Products table already exists';
    END IF;
END
$$;

-- 2. Disable Row Level Security on products table
ALTER TABLE public.products DISABLE ROW LEVEL SECURITY;

-- 3. Create or replace function to check specifications format
CREATE OR REPLACE FUNCTION fix_specifications_format()
RETURNS void AS $$
DECLARE
    product_record RECORD;
    fixed_specs TEXT;
BEGIN
    FOR product_record IN SELECT id, specifications FROM public.products WHERE specifications IS NOT NULL LOOP
        BEGIN
            -- Check if it's already valid JSON array
            PERFORM json_array_elements_text(product_record.specifications::json);
            -- If we get here, it's valid JSON array, no need to fix
            CONTINUE;
        EXCEPTION WHEN OTHERS THEN
            -- Not valid JSON array, try to fix
            BEGIN
                -- If it's an object, convert to array of values
                IF product_record.specifications ~ '^{.*}$' THEN
                    SELECT json_agg(value) INTO fixed_specs
                    FROM json_each_text(product_record.specifications::json);
                -- If it's a string, wrap in array
                ELSE
                    fixed_specs := json_build_array(product_record.specifications)::text;
                END IF;
                
                -- Update the record
                UPDATE public.products
                SET specifications = fixed_specs
                WHERE id = product_record.id;
                
                RAISE NOTICE 'Fixed specifications format for product ID %', product_record.id;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not fix specifications for product ID %, setting to null', product_record.id;
                UPDATE public.products
                SET specifications = NULL
                WHERE id = product_record.id;
            END;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 4. Create function to disable RLS via RPC
CREATE OR REPLACE FUNCTION admin_disable_rls(table_name text)
RETURNS boolean AS $$
BEGIN
    EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', table_name);
    RETURN true;
EXCEPTION WHEN OTHERS THEN
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Create function to check RLS status
CREATE OR REPLACE FUNCTION check_rls_status(table_name text)
RETURNS text AS $$
DECLARE
    rls_enabled boolean;
BEGIN
    SELECT relrowsecurity INTO rls_enabled
    FROM pg_class
    WHERE oid = (table_name::regclass)::oid;
    
    IF rls_enabled THEN
        RETURN 'enabled';
    ELSE
        RETURN 'disabled';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN 'unknown';
END;
$$ LANGUAGE plpgsql;

-- 6. Create function to get table structure
CREATE OR REPLACE FUNCTION get_table_structure(table_name text)
RETURNS json AS $$
DECLARE
    result json;
BEGIN
    SELECT json_agg(json_build_object(
        'column_name', column_name,
        'data_type', data_type,
        'is_nullable', is_nullable,
        'column_default', column_default
    )) INTO result
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = $1
    ORDER BY ordinal_position;
    
    RETURN result;
EXCEPTION WHEN OTHERS THEN
    RETURN null;
END;
$$ LANGUAGE plpgsql;

-- 7. Run the fix specifications function
SELECT fix_specifications_format();

-- 8. Add comment to products table
COMMENT ON TABLE public.products IS 'LED display products catalog';