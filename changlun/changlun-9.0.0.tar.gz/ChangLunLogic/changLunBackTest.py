from ChangLunLogic.ChangLun import ChangLun

def getHistTradeFeatures(df,windows=250):
    featureList = []
    sellPointList = []
    if len(df) < 250:
        return []
    for i in range(len(df)-windows+1):
        tempDf = df.iloc[i:i+windows]
        model = ChangLun(tempDf,'D','M')
        isRun = model.run(True)
        if not isRun:
            continue
        isBuy = model.isPenBuyPoint()
        if isBuy:
            feature = model.genFeature()
            featureList.append(feature)
        if model.isPenSellPoint():
            sellPoint = model.genPenSellFeature()
            sellPointList.append(sellPoint)
    featureList = markFeautures(featureList, sellPointList,df)
    return featureList

def markFeautures( featureList, sellPointList, df ):
    if featureList is None or len(featureList) == 0:
        return []
    model = ChangLun(df,'D','M')
    model.run()
    lastPen = model.penList[-1]
    penSet = set([x['endDate'] for x in model.penList[0:-1]])
    for feature in featureList:
        tradeDate = feature['trade_date']
        penEndDate = feature['pen_end_date']
        isTruePen = penSet.__contains__(penEndDate)
        isLastPen = (penEndDate == lastPen['endDate'])
        feature['label_is_pen_true'] = None if isLastPen else isTruePen
        feature['label_is_last_pen'] = isLastPen
        sellPoint = None
        for tmp in sellPointList:
            if tmp['sell_before_pen_date'] == penEndDate:
                sellPoint = tmp
                break
        buyHistIndex = model.getHistDataIndexFromDate(tradeDate) + 1

        # 买点为当下
        if buyHistIndex >= len(model.histData):
            feature['buy_date'] = None
            feature['buy_value'] = None
            feature['sell_date'] = None
            feature['sell_value'] = None
            feature['sell_profit'] = None
            feature['sell_hold_num'] = None
            feature['label_is_trade_success'] = None
            continue
        else:
            isPenBroken = False
            feature['buy_date'] = model.histData[buyHistIndex]['date']
            feature['buy_value'] = model.histData[buyHistIndex]['open']
            if sellPoint is not None:
                # 被向上笔破坏
                isPenBroken = True
                feature['sell_date'] = sellPoint['sell_date']
                feature['sell_value'] = sellPoint['sell_value']
            else:
                for i in range(buyHistIndex,len(model.histData)):
                    # 向下破低点
                    if model.histData[i]['low'] < feature['buy_pen_value']:
                        isPenBroken = True
                        feature['sell_date'] = model.histData[i]['date']
                        feature['sell_value'] = model.histData[i]['close']
                        break
            if isPenBroken:
                feature['sell_profit'] = (feature['sell_value'] - feature['buy_value']) / (feature['buy_value']) * 100
                feature['sell_hold_num'] = i - buyHistIndex
                feature['label_is_trade_sucess'] = feature['sell_profit'] > 0
            else:
                feature['buy_date'] = None
                feature['buy_value'] = None
                feature['sell_date'] = None
                feature['sell_value'] = None
                feature['sell_profit'] = None
                feature['sell_hold_num'] = None
                feature['label_is_trade_success'] = None

    return featureList
