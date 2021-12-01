def generate_bids(gen,initial_disp,date,market):
    # This function generates bids using the predicted dispatch and costs, in
    # combination with forecasting
    n_g = len(gen)
    if len(list(market.keys()))>0:
        n_m = len(market['next_closing_time'])
        bid = [[0 for i in range(len(initial_disp)-1)] for j in range(3)] #Bids have 3 parts - capacity, cost, and timestamp

        SP = get_spot_price(gen,date[0])
        RT = market_forecast(gen,date[1])
        #Assuming 1 market connection - update for more than 1 market
        Pgrid_est = [0 for t in range(len(initial_disp[0])-1)]
        for i in range(n_g):
            if (gen[i]['type']=='Utility' and gen[i]['source'] == 'Electricity') or gen[i]['type'] == 'Market':
                Pgrid_est = [Pgrid_est[t] + initial_disp[i][t+1] for t in range(len(initial_disp[0])-1)]#The estimated external supply needed from market = Pspot + Pmarket
        for i in range(n_m):
            if market['type'] =='Real-Time': #will be generating bids for the Real-time market
                market['m_lambda'][i].append(get_market_lambda(SP,RT[i])) #Compare market price 1 hour ahead, to current spot price to determine lambda
                if market['strategy'][i] =='Price-Taker':
                    for j in range(len(Pgrid_est)):
                        if Pgrid_est[j]>=0: #If buying from market, bid $0 to ensure bid is accepted
                            bid[0][j] = Pgrid_est[j]*market['m_lambda'][i][-1]
                            bid[1][j] = 0
                            bid[2][j] = date[j]
                        else: #If selling to market, bid inf to ensure bid is accepted
                            bid[0][j] = Pgrid_est[j]*market['m_lambda'][i][-1]
                            bid[1][j] = float('inf')
                            bid[2][j] = date[j]
                else:
                    pass
                    #Price-Maker strategy would go here
            elif market['type'][i] =='Day-Ahead':
                pass
            #Add here for Day-Ahead
        market = bid_cap_forecast(bid,market,date[0])

        #send bids to market
        market = submit_bid(bid,market)
    return market

def submit_bid(forecast_bid,market):
    #This function simulates the sending of bids to a connected to market

    bid_hour = market['next_closing_time']
    bid = 0
    _,bid,_ = intersect([round(forecast_bid[t][3],5) for t in range(len(forecast_bid))],round(bid_hour,5)) #Get the time the next bid needs to be submitted, round to the 5th decimal

    #add submitted bid to market struct
    if len(bid)>0:
        market['bid']['capacity'].append(forecast_bid[0][bid])
        market['bid']['price'].append(forecast_bid[1][bid])
        market['bid']['time'].append(forecast_bid[2][bid])
    return market

def get_market_lambda(market_price,spot_price):
    #This function calculates the ratio lambda based off of current market and
    #spot prices

    #place holder lambda until ideal ratio is found
    m_lambda = 3/5 #3/5 from scheduled market, 2/5 from spot market

    return m_lambda

def bid_cap_forecast(bid,market,time):
    #This function updates the forecasted bids, knowing that the current time and
    #the next hour have committed awards

    #Initial disp does not have any awarded capacity for the first 2 hours, so
    #assign times
    if len(market['award']['capacity'])==0:
        market['award']['capacity'].append(0)
        market['award']['capacity'].append(0)
        market['award']['time'].append(time)
        market['award']['time'].append(time+(1/24)) #+1hour in datenum
        market['award']['price'].append(0)
        market['award']['price'].append(0)

    if len(market['award']['capacity'])>0: #If bids have been awarded
        _,award_num,bid_num = intersect(market['award']['time'],bid[2]) #Find indices where award time = time within bid horizon
        for k in range(len(award_num)):
            bid[0][bid_num[k]] = market['award']['capacity'][award_num[k]]
            bid[1][bid_num[k]] = market['award']['price'][award_num[k]]
            bid[2][bid_num[k]] = market['award']['time'][award_num[k]]


    market['forecast']['capacity'] = bid[0]
    market['forecast']['price'] = bid[1]
    market['forecast']['time'] = bid[2]
    return market

def get_spot_price(gen,date):
    #TODO creat this function
    sp = 0.05
    return sp

def market_forecast(gen,date):
    #TODO creat this function
    rt = [0.05 for t in range(len(date))]
    return rt

def intersect(time,bid):
    #TODO creat this function
    a = 1
    award_num = [2]
    bid_num = [3]
    return a,award_num,bid_num