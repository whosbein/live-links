select t1.l_id, t2a.name as source, t2b.name as target from link as t1 join file as t2a on t2a.f_id = t1.s_id join file as t2b on t2b.f_id = t1.t_id;

