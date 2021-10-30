import pandas as pd
#pd.set_option("display.max_columns", 999)

fb_annual = pd.read_pickle('data/fb_annual.pickle')
aapl_annual = pd.read_pickle('data/aapl_annual.pickle')
amzn_annual = pd.read_pickle('data/amzn_annual.pickle')

class DCF:
    def __init__(self, df, perds=20):
        self.Periods = perds
        self.Revenue = df['Revenue'].astype('float')
        self.Revenue_per_share = df['Revenue per Share'].astype('float')
        self.EBIT = df['EBIT'].astype('float')
        self.FCF_per_share = df['Free Cash Flow per Share'].astype('float')
        self.SharePrice = df['Month End Stock Price'].astype('float') 

    def avg_rev_growth(self, periods=6):
        return self.Revenue.tail(periods).pct_change().mean()

    def avg_ebit_margin(self, periods=5):
        return (self.EBIT.tail(periods) / self.Revenue.tail(periods)).mean()

    def avg_fcf_growth(self, periods=6):
        return self.FCF_per_share.tail(periods).pct_change().mean()

    def projected_fcf_per_share(self):
        return [float(fb.FCF_per_share.tail(1).values) * ((1 + fb.avg_fcf_growth())**i) for i in list(range(0, self.Periods))][1:]

# Temp -- using avg revenue growth not avg revenue per share growth rate
    def projected_rev_per_share(self):
        return [float(self.Revenue_per_share.tail(1).values) * ((1 + self.avg_rev_growth())**i) for i in list(range(0, self.Periods))][1:]

    def discount_factors(self, cost_of_cap):
        x = []
        tmp = list(range(1, self.Periods))
        for i in tmp:
            x.append((1 / (1  + cost_of_cap) **i))
        return x

    def terminal_value(ebit_val, cost_of_capital=0.08, growth_rate=0.03):
        ebit_value = ebit_val * (1 + growth_rate)
        return float(ebit_value / cost_of_capital)

    def model(self):
        rev = pd.Series(self.projected_rev_per_share())
        ebit = pd.Series(rev * self.avg_ebit_margin())
        fcf = self.projected_fcf_per_share()
        dis_facs = self.discount_factors(.08)
        share_price = self.SharePrice.iloc[-1].values[0]
        d = dict(Revenue=rev, EBIT=ebit, FreeCashFlow=fcf,
                DiscountFactor=dis_facs, SharePrice=share_price)
        df = pd.DataFrame(d)
        df['Terminal_Value'] = df['EBIT'] / 0.08
        df['Cummulative_FCF'] = df['FreeCashFlow'].cumsum()
        df['PV_Cum_FCF'] = df['Cummulative_FCF'] * df['DiscountFactor']
        df['PV_Term_Val'] = df['Terminal_Value'] * df['DiscountFactor']
        df['EV'] = df['PV_Term_Val'] + df['PV_Cum_FCF']
        return df




fb = DCF(fb_annual)
model = fb.model()
fb_final = model[model['EV'] <= model['SharePrice']]

print(fb_final, '\n\nThe market implied competitive advantage periods for FB is {} years.\n'.format(len(fb_final)))


aapl = DCF(aapl_annual)
model = aapl.model()
aapl_final = model[model['EV'] <= model['SharePrice']]
print(aapl_final, '\n\nThe market implied competitive advantage periods for AAPL is {} years.\n'.format(len(aapl_final)))



amzn = DCF(amzn_annual)
model = amzn.model()
amzn_final = model[model['EV'] <= model['SharePrice']]
print(amzn_final, '\n\nThe market implied competitive advantage periods for AMZN is {} years.\n'.format(len(amzn_final)))


