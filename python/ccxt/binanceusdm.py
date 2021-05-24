# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.binance import binance
from ccxt.base.errors import BadRequest


class binanceusdm(binance):

    def describe(self):
        return self.deep_extend(super(binanceusdm, self).describe(), {
            'id': 'binanceusdm',
            'name': 'Binance USDⓈ-M',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/117738721-668c8d80-b205-11eb-8c49-3fad84c4a07f.jpg',
            },
            'has': {
                'fetchPositions': True,
                'fetchIsolatedPositions': True,
                'fetchFundingRate': True,
                'fetchFundingHistory': True,
                'setLeverage': True,
                'setMode': True,
            },
            'options': {
                'defaultType': 'future',
                # https://www.binance.com/en/support/faq/360033162192
                # tier amount, maintenance margin, initial margin
                'leverageBrackets': None,
                'marginTypes': {},
            },
            # https://www.binance.com/en/fee/futureFee
            'fees': {
                'trading': {
                    'tierBased': True,
                    'percentage': True,
                    'taker': self.parse_number('0.000400'),
                    'maker': self.parse_number('0.000200'),
                    'tiers': {
                        'taker': [
                            [self.parse_number('0'), self.parse_number('0.000400')],
                            [self.parse_number('250'), self.parse_number('0.000400')],
                            [self.parse_number('2500'), self.parse_number('0.000350')],
                            [self.parse_number('7500'), self.parse_number('0.000320')],
                            [self.parse_number('22500'), self.parse_number('0.000300')],
                            [self.parse_number('50000'), self.parse_number('0.000270')],
                            [self.parse_number('100000'), self.parse_number('0.000250')],
                            [self.parse_number('200000'), self.parse_number('0.000220')],
                            [self.parse_number('400000'), self.parse_number('0.000200')],
                            [self.parse_number('750000'), self.parse_number('0.000170')],
                        ],
                        'maker': [
                            [self.parse_number('0'), self.parse_number('0.000200')],
                            [self.parse_number('250'), self.parse_number('0.000160')],
                            [self.parse_number('2500'), self.parse_number('0.000140')],
                            [self.parse_number('7500'), self.parse_number('0.000120')],
                            [self.parse_number('22500'), self.parse_number('0.000100')],
                            [self.parse_number('50000'), self.parse_number('0.000080')],
                            [self.parse_number('100000'), self.parse_number('0.000060')],
                            [self.parse_number('200000'), self.parse_number('0.000040')],
                            [self.parse_number('400000'), self.parse_number('0.000020')],
                            [self.parse_number('750000'), self.parse_number('0')],
                        ],
                    },
                },
            },
        })

    def fetch_trading_fees(self, params={}):
        self.load_markets()
        marketSymbols = list(self.markets.keys())
        fees = {}
        accountInfo = self.fapiPrivateGetAccount(params)
        # {
        #     "feeTier": 0,       # account commisssion tier
        #     "canTrade": True,   # if can trade
        #     "canDeposit": True,     # if can transfer in asset
        #     "canWithdraw": True,    # if can transfer out asset
        #     "updateTime": 0,
        #     "totalInitialMargin": "0.00000000",    # total initial margin required with current mark price(useless with isolated positions), only for USDT asset
        #     "totalMaintMargin": "0.00000000",     # total maintenance margin required, only for USDT asset
        #     "totalWalletBalance": "23.72469206",     # total wallet balance, only for USDT asset
        #     "totalUnrealizedProfit": "0.00000000",   # total unrealized profit, only for USDT asset
        #     "totalMarginBalance": "23.72469206",     # total margin balance, only for USDT asset
        #     "totalPositionInitialMargin": "0.00000000",    # initial margin required for positions with current mark price, only for USDT asset
        #     "totalOpenOrderInitialMargin": "0.00000000",   # initial margin required for open orders with current mark price, only for USDT asset
        #     "totalCrossWalletBalance": "23.72469206",      # crossed wallet balance, only for USDT asset
        #     "totalCrossUnPnl": "0.00000000",      # unrealized profit of crossed positions, only for USDT asset
        #     "availableBalance": "23.72469206",       # available balance, only for USDT asset
        #     "maxWithdrawAmount": "23.72469206"     # maximum amount for transfer out, only for USDT asset
        #     ...
        # }
        feeTier = self.safe_integer(accountInfo, 'feeTier')
        feeTiers = self.fees['trading']['tiers']
        maker = feeTiers['maker'][feeTier][1]
        taker = feeTiers['taker'][feeTier][1]
        for i in range(0, len(marketSymbols)):
            symbol = marketSymbols[i]
            fees[symbol] = {
                'info': {
                    'feeTier': feeTier,
                },
                'symbol': symbol,
                'maker': maker,
                'taker': taker,
            }
        return fees

    def transfer_in(self, code, amount, params={}):
        # transfer from spot wallet to usdm futures wallet
        return self.futuresTransfer(code, amount, 1, params)

    def transfer_out(self, code, amount, params={}):
        # transfer from usdm futures wallet to spot wallet
        return self.futuresTransfer(code, amount, 2, params)

    def fetch_funding_rate(self, symbol=None, params={}):
        self.load_markets()
        market = None
        request = {}
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        response = self.fapiPublicGetPremiumIndex(self.extend(request, params))
        #
        #   {
        #     "symbol": "BTCUSDT",
        #     "markPrice": "45802.81129892",
        #     "indexPrice": "45745.47701915",
        #     "estimatedSettlePrice": "45133.91753671",
        #     "lastFundingRate": "0.00063521",
        #     "interestRate": "0.00010000",
        #     "nextFundingTime": "1621267200000",
        #     "time": "1621252344001"
        #  }
        #
        if isinstance(response, list):
            result = []
            values = list(response.values())
            for i in range(0, len(values)):
                parsed = self.parseFundingRate(values[i])
                result.append(parsed)
            return result
        else:
            return self.parseFundingRate(response)

    def load_leverage_brackets(self, reload=False, params={}):
        self.load_markets()
        # by default cache the leverage bracket
        # it contains useful stuff like the maintenance margin and initial margin for positions
        if (self.options['leverageBrackets'] is None) or (reload):
            response = self.fapiPrivateGetLeverageBracket(params)
            self.options['leverageBrackets'] = {}
            for i in range(0, len(response)):
                entry = response[i]
                marketId = self.safe_string(entry, 'symbol')
                symbol = self.safe_symbol(marketId)
                brackets = self.safe_value(entry, 'brackets')
                result = []
                for j in range(0, len(brackets)):
                    bracket = brackets[j]
                    # we use floats here internally on purpose
                    notionalFloor = self.safe_float(bracket, 'notionalFloor')
                    maintenanceMarginPercentage = self.safe_string(bracket, 'maintMarginRatio')
                    result.append([notionalFloor, maintenanceMarginPercentage])
                self.options['leverageBrackets'][symbol] = result
        return self.options['leverageBrackets']

    def fetch_positions(self, symbols=None, params={}):
        self.load_markets()
        self.load_leverage_brackets()
        account = self.fapiPrivateGetAccount(params)
        result = self.parseAccountPositions(account)
        if symbols is None:
            return result
        else:
            return self.filter_by_array(result, 'symbol', symbols, False)

    def fetch_isolated_positions(self, symbol=None, params={}):
        # only supported in usdm futures
        self.load_markets()
        self.load_leverage_brackets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        response = self.fapiPrivateGetPositionRisk(self.extend(request, params))
        if symbol is None:
            result = []
            for i in range(0, len(response)):
                parsed = self.parsePositionRisk(response[i], market)
                if parsed['marginType'] == 'isolated':
                    result.append(parsed)
            return result
        else:
            return self.parsePositionRisk(self.safe_value(response, 0), market)

    def fetch_funding_history(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        # "TRANSFER"，"WELCOME_BONUS", "REALIZED_PNL"，"FUNDING_FEE", "COMMISSION" and "INSURANCE_CLEAR"
        request = {
            'incomeType': 'FUNDING_FEE',
        }
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        if since is not None:
            request['startTime'] = since
        if limit is not None:
            request['limit'] = limit
        response = self.fapiPrivateGetIncome(self.extend(request, params))
        return self.parseIncomes(response, market, since, limit)

    def set_leverage(self, symbol, leverage, params={}):
        # WARNING: THIS WILL INCREASE LIQUIDATION PRICE FOR OPEN ISOLATED LONG POSITIONS
        # AND DECREASE LIQUIDATION PRICE FOR OPEN ISOLATED SHORT POSITIONS
        if (leverage < 1) or (leverage > 125):
            raise BadRequest(self.id + ' leverage should be between 1 and 125')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'leverage': leverage,
        }
        return self.fapiPrivatePostLeverage(self.extend(request, params))

    def set_mode(self, symbol, marginType, params={}):
        #
        # {"code": -4048 , "msg": "Margin type cannot be changed if there exists position."}
        #
        # or
        #
        # {"code": 200, "msg": "success"}
        #
        marginType = marginType.upper()
        if (marginType != 'ISOLATED') and (marginType != 'CROSSED'):
            raise BadRequest(self.id + ' marginType must be either isolated or crossed')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'marginType': marginType,
        }
        return self.fapiPrivatePostMarginType(self.extend(request, params))
