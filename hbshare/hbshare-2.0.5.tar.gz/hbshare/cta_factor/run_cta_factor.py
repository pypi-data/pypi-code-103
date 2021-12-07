if __name__ == '__main__':
    from db_cons import sql_write_path_work, sql_user_work
    from hbshare.cta_factor.hsjy_to_local import (
        hsjy_fut_pro_info,
        hsjy_fut_wr,
        hsjy_fut_com_info,
        hsjy_fut_com,
        hsjy_fut_member,
    )
    from hbshare.cta_factor.hsjy_func import hsjy_fut_index
    from hbshare.cta_factor.factor_index import run
    from hbshare.cta_factor.factor_func import index_gen

    hsjy_fut_pro_info(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_wr(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_com_info(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_com(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_member(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    hsjy_fut_index(
        db_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
    run(sql_path=sql_write_path_work['daily'])
    index_gen(
        sql_path=sql_write_path_work['daily'],
        sql_info=sql_user_work
    )
