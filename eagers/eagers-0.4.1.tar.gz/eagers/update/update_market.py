def update_market(gen,market,date):
    market = {}
    # if ~isempty(market)
    #     n_m = length(market.next_closing_time);
    # else
    #     n_m = 0;
    # end
    # for i = 1:1:n_m
    #     if nnz([date(1),date(2)]>=market.next_closing_time(i)) %date(2) is hard coded but should reflect the bidding window
    #         %Right now currently submitting bids 2 hours ahead, so need to
    #         %update every hour to update the awards
    #         if strcmp(market.type{i},'Day-Ahead')
    #             %update closing price
    #             market.closing_price(end+1:end+24,i) =  market_forecast(gen,date); %currently fixed, but should pull from a time series or function
    #             %award bids
    #             if strcmp(market.strategy{i}, 'Price-Taker')
    #                 market.award.time(end+1:end+24,i) = market.bid.time(end-23:end,i);
    #                 market.award.price(end+1:end+24,i) = market.closing_price(end-23:end,i);
    #                 market.award.capacity(end+1:end+24,i) = market.bid.capacity(end-23:end,i);
    #             end
    #         elseif strcmp(market.type{i},'Real-Time')
    #             %update closing price
    #             market.closing_price(end+1,i) =  market_forecast(gen,date(1)); %pulls from a time series 
    #             %award bids
    #             if strcmp(market.strategy{i}, 'Price-Taker')
    #                 [~,new_award] = intersect(round(market.bid.time,5),round(market.next_closing_time,5)); %find the index of the submitted bid
    #                 market.award.time(end+1,i) = market.bid.time(new_award,i);
    #                 market.award.price(end+1,i) = market.closing_price(new_award,i);
    #                 market.award.capacity(end+1,i) = market.bid.capacity(new_award,i);
    #             end
    #         end
                    
    #         %update next closing time
    #         while date(2)>=market.next_closing_time(i)
    #             if strcmp(market.type{i},'Day-Ahead')
    #                 market.next_closing_time(i) = market.next_closing_time(i) + 1;  
    #             elseif strcmp(market.type{i},'Real-Time')
    #                 market.next_closing_time(i) = market.next_closing_time(i) + 1/24; %hard coded for now, need to update later
    return market