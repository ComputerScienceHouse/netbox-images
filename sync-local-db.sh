PGPASSWORD=$REMOTE_PG_PASS pg_dump -h postgres.csh.rit.edu -p 5432 -U netbox netbox | PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -p 5432 -U netbox netbox
