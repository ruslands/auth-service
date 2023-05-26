INSERT INTO auth.linkroleuser (user_id, role_id)
SELECT u.id, r.id
FROM (VALUES
('test@test.com', 'manager')
) AS pairs (email, role_title)
JOIN auth.user u ON u.email = pairs.email
JOIN auth.role r ON r.title = pairs.role_title;
