import kabutobashi as kb


def test_workday():
    date_list = kb.get_past_n_days("2020-03-31", 30)
    assert len(date_list) == 30
    # 祝日が除かれていることを確認
    assert "2020-03-20" not in date_list
    # 土日が除かれていることを確認
    assert "2020-03-07" not in date_list
    assert "2020-03-08" not in date_list
    assert "2020-03-14" not in date_list
    assert "2020-03-15" not in date_list
    assert "2020-03-21" not in date_list
    assert "2020-03-22" not in date_list
    assert "2020-03-28" not in date_list
    assert "2020-03-29" not in date_list
