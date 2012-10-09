/* select that displays all links but uses the file name pulled from file table */
select t1.l_id, t2a.name as source, t2b.name as target from link as t1 join file as t2a on t2a.f_id = t1.s_id join file as t2b on t2b.f_id = t1.t_id;

/* same thing as above, only now specifying a source link id */
select t1.l_id, t2a.name as source, t2b.name as target from link as t1 join file as t2a on t2a.f_id = t1.s_id join file as t2b on t2b.f_id = t1.t_id where t1.s_id = ID;

/* select that grabs the menu id that corresponds to the index id that is its root */
select t1.f_id as index_id, t2.f_id as menu_id from file as t1 join file as t2 where t1.name = "index.php" and t2.name = "menu.php" and t1.depth = t2.depth and t1.path = t2.path;

/* select that gives the size of files that aren't live (wasted space) */
select sum(size) as bytes, round(sum(size) / 1048576.0, 2) as megabytes, round(sum(size) / 1073741824.0, 2) as gigabytes from file where live = 0;

/* select that shows percentage of space that is used by files that aren't linked to */
select (round(((select sum(size) from file where live = 0) / 1.0) / (select sum(size) from file), 4) * 100) || '%' as wasted;
