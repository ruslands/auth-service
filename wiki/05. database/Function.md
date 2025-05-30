# clean_changelog()

SELECT * FROM core.card WHERE jsonb_array_length(changelog) > 0;
SELECT core.clean_changelog();

SELECT * FROM auth.user WHERE jsonb_array_length(changelog) > 0;
SELECT auth.clean_changelog();