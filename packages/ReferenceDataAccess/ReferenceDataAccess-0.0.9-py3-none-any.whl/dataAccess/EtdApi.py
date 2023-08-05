# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 10:44:00 2020

@author: Sangoi
"""

import requests
import json
import pandas as pd
from dataAccess.EquityApi import EquityApi


class EtdApi(object):
    
    """
    This class hold all methods to access etd (derivatives - futures/options/strategies) data
      
    """
    
    def __init__(self, key):
        """ 
        Initialize the class
        Keyword Arguments:
            key:  RDUAccess api key

        """
        
        self.key = key
        self.all_column_list = ["ct_exchCd","ct_lstngCycleTp","ct_omic","ct_segTp","ct_smic","ct_tckSz","ct_tckVal","ct_trdStsTp","ct_vndrExchCd","ct_ticker","ct_bbgIdBbGlobal","ct_rduSecId","ct_rduSegId","ct_bbgCompositeIdBbGlobal","ct_rduSecIdExp","ct_rduSegIdExp","ct_gmiFullPrdCd","p_name","p_roundLotSz","p_clrngCd","p_name","p_roundLotSz","p_trdCtyCd","p_trdCcyMajorFl","p_trdCcyCd","p_dayNum","p_maxOrdSz","p_tckSzDnmntr","p_prdTp","p_flexElgblFl","p_clrngCcyCd","p_msrmntUntCd","p_tckSzNmrtr","p_spotMnthPosLmt","p_mnthPosLmt","p_allMnthPosLmt","p_blckTrdElgblFl","p_actFl","p_exchCd","p_wkNum","p_exchRptngLvl","p_cftcRptngLvl","p_trdStsTp","p_cftcRegFl","p_undlRltnsTp","p_clrngCd","p_rduPrdId","c_name","c_assetTp","c_expDt","c_lstTrdDt","c_settleDt","c_frstDlvryDt","c_frstNtcDt","c_lstDlvryDt","c_name","c_vndrAssetTp","c_prntAssetTp","c_strikePx","c_cfi","c_yrCd","c_settleTp","c_ctrSz","c_frstTrdDt","c_settleFixDt","c_numOfLegs","c_accrlStrtDt","c_accrlEndDt","c_mnthCd","c_dayNum","c_pntVal","c_flexFl","c_actFl","c_wkNum","c_lstNtcDt","c_trdStsTp","c_cfiCd","c_isin","c_bbgTicker","c_bbgIdBbUnique","c_aiiCode","ct_ric","ct_trAssetId","ct_trQuoteId","p_ricRoot","p_u_name","p_u_ric","p_u_ticker","p_u_isin","p_u_rduSecId","p_exchPrfx"] 
 


    def __get_underlying_data(self, isin, exchange):
        equity = EquityApi(key=self.key)
        underlyingData = equity.get_by_isin_exchange(isin, exchange)
        #underlyingData = underlyingData.add_prefix('u_')
        return underlyingData
           

    def __convert_json_to_df(self, input_key,json_data, fetchUnderlying:False, columnList=[]):
        df = pd.json_normalize(json_data)        
        msg = df.get('message')
        product_dict = {}
        if(not columnList):
            columnList.extend(self.all_column_list)
        if (isinstance(msg, pd.Series)):
            message = msg.loc[0]
            contract_dict = {}
            contract_dict['success'] = False
            contract_dict['failed_message'] = message
            product_dict[input_key] = contract_dict
        else:
            for index, row in df.iterrows():
                """product_list.append(row['basics.name'])
                product_list.append(row['basics.roundLotSz'])
                product_list.append(row['ids.clrngCd'])
                """
    
                contracts = row.get('contracts')
                for contract in contracts :
                    
                    contract_dict = {}
    
                    
                    c_tradelines = contract['tradeLines']['tradeLine']
                    
                          
                    for c_tradeline in c_tradelines :
                        ct_basics = c_tradeline['basics']
                        
                        contract_dict['success'] = True
                        
                        if(	'ct_exchCd'	in	columnList):	contract_dict['ct_exchCd'] =ct_basics.get('exchCd')
                        if(	'ct_lstngCycleTp'	in	columnList):	contract_dict['ct_lstngCycleTp'] =ct_basics.get('lstngCycleTp')
                        if(	'ct_omic'	in	columnList):	contract_dict['ct_omic'] =ct_basics.get('omic')
                        if(	'ct_segTp'	in	columnList):	contract_dict['ct_segTp'] =ct_basics.get('segTp')
                        if(	'ct_smic'	in	columnList):	contract_dict['ct_smic'] =ct_basics.get('smic')
                        if(	'ct_tckSz'	in	columnList):	contract_dict['ct_tckSz'] =ct_basics.get('tckSz')
                        if(	'ct_tckVal'	in	columnList):	contract_dict['ct_tckVal'] =ct_basics.get('tckVal')
                        if(	'ct_trdStsTp'	in	columnList):	contract_dict['ct_trdStsTp'] =ct_basics.get('trdStsTp')

                        ct_sessions = c_tradeline['sessions'].get('session')
                        ct_session = ct_sessions[0]
                        ct_session_id = ct_session.get('ids')
                        #print(type(ct_session_id))
                        #print(ct_session_id)
                        if(	'ct_ric'	in	columnList):	contract_dict['ct_ric'] =ct_session_id.get('ric')
                        if(	'ct_trAssetId'	in	columnList):	contract_dict['ct_trAssetId'] =ct_session_id.get('trAssetId')
                        if(	'ct_trQuoteId'	in	columnList):	contract_dict['ct_trQuoteId'] =ct_session_id.get('trQuoteId')                        


                        #contract_dict['ct_vndrExchCd'] =ct_basics.get('vndrExchCd')
    
                        ct_ids = c_tradeline['ids']
                        
                        if(	'ct_ticker'	in	columnList):	contract_dict['ct_ticker']=ct_ids.get('ticker')
                        if(	'ct_bbgIdBbGlobal'	in	columnList):	contract_dict['ct_bbgIdBbGlobal']=ct_ids.get('bbgIdBbGlobal')
                        if(	'ct_rduSecId'	in	columnList):	contract_dict['ct_rduSecId']=ct_ids.get('rduSecId')
                        if(	'ct_rduSegId'	in	columnList):	contract_dict['ct_rduSegId']=ct_ids.get('rduSegId')
                        if(	'ct_bbgCompositeIdBbGlobal'	in	columnList):	contract_dict['ct_bbgCompositeIdBbGlobal']=ct_ids.get('bbgCompositeIdBbGlobal')
                        if(	'ct_rduSecIdExp'	in	columnList):	contract_dict['ct_rduSecIdExp']=ct_ids.get('rduSecIdExp')
                        if(	'ct_rduSegIdExp'	in	columnList):	contract_dict['ct_rduSegIdExp']=ct_ids.get('rduSegIdExp')
                        if(	'ct_gmiFullPrdCd'	in	columnList):	contract_dict['ct_gmiFullPrdCd']=ct_ids.get('gmiFullPrdCd')
 
                        if(	'p_name'	in	columnList):	contract_dict['p_name'] = row.get('basics.name')
                        if(	'p_roundLotSz'	in	columnList):	contract_dict['p_roundLotSz'] = row.get('basics.roundLotSz')
                        if(	'p_clrngCd'	in	columnList):	contract_dict['p_clrngCd'] = row.get('ids.clrngCd')
                        if(	'p_name'	in	columnList):	contract_dict['p_name'] =row.get('basics.name')
                        if(	'p_roundLotSz'	in	columnList):	contract_dict['p_roundLotSz'] =row.get('basics.roundLotSz')
                        if(	'p_trdCtyCd'	in	columnList):	contract_dict['p_trdCtyCd'] =row.get('basics.trdCtyCd')
                        if(	'p_trdCcyMajorFl'	in	columnList):	contract_dict['p_trdCcyMajorFl'] =row.get('basics.trdCcyMajorFl')
                        if(	'p_trdCcyCd'	in	columnList):	contract_dict['p_trdCcyCd'] =row.get('basics.trdCcyCd')
                        if(	'p_dayNum'	in	columnList):	contract_dict['p_dayNum'] =row.get('basics.dayNum')
                        if(	'p_maxOrdSz'	in	columnList):	contract_dict['p_maxOrdSz'] =row.get('basics.maxOrdSz')
                        if(	'p_tckSzDnmntr'	in	columnList):	contract_dict['p_tckSzDnmntr'] =row.get('basics.tckSzDnmntr')
                        if(	'p_prdTp'	in	columnList):	contract_dict['p_prdTp'] =row.get('basics.prdTp')
                        if(	'p_flexElgblFl'	in	columnList):	contract_dict['p_flexElgblFl'] =row.get('basics.flexElgblFl')
                        if(	'p_clrngCcyCd'	in	columnList):	contract_dict['p_clrngCcyCd'] =row.get('basics.clrngCcyCd')
                        if(	'p_msrmntUntCd'	in	columnList):	contract_dict['p_msrmntUntCd'] =row.get('basics.msrmntUntCd')
                        if(	'p_tckSzNmrtr'	in	columnList):	contract_dict['p_tckSzNmrtr'] =row.get('basics.tckSzNmrtr')
                        if(	'p_spotMnthPosLmt'	in	columnList):	contract_dict['p_spotMnthPosLmt'] =row.get('basics.spotMnthPosLmt')
                        if(	'p_mnthPosLmt'	in	columnList):	contract_dict['p_mnthPosLmt'] =row.get('basics.mnthPosLmt')
                        if(	'p_allMnthPosLmt'	in	columnList):	contract_dict['p_allMnthPosLmt'] =row.get('basics.allMnthPosLmt')
                        if(	'p_blckTrdElgblFl'	in	columnList):	contract_dict['p_blckTrdElgblFl'] =row.get('basics.blckTrdElgblFl')
                        if(	'p_actFl'	in	columnList):	contract_dict['p_actFl'] =row.get('basics.actFl')
                        if(	'p_exchCd'	in	columnList):	contract_dict['p_exchCd'] =row.get('basics.exchCd')
                        if(	'p_wkNum'	in	columnList):	contract_dict['p_wkNum'] =row.get('basics.wkNum')
                        if(	'p_exchRptngLvl'	in	columnList):	contract_dict['p_exchRptngLvl'] =row.get('basics.exchRptngLvl')
                        if(	'p_cftcRptngLvl'	in	columnList):	contract_dict['p_cftcRptngLvl'] =row.get('basics.cftcRptngLvl')
                        if(	'p_trdStsTp'	in	columnList):	contract_dict['p_trdStsTp'] =row.get('basics.trdStsTp')
                        if(	'p_cftcRegFl'	in	columnList):	contract_dict['p_cftcRegFl'] =row.get('basics.cftcRegFl')
                        if(	'p_undlRltnsTp'	in	columnList):	contract_dict['p_undlRltnsTp'] =row.get('basics.undlRltnsTp')
                        if(	'p_clrngCd'	in	columnList):	contract_dict['p_clrngCd'] =row.get('ids.clrngCd')
                        if(	'p_rduPrdId'	in	columnList):	contract_dict['p_rduPrdId'] =row.get('ids.rduPrdId')

                        prd_tradeline = row.get('tradeLines.tradeLine')
                        if(	'p_exchPrfx'	in	columnList):	contract_dict['p_exchPrfx'] = prd_tradeline[0].get('ids').get('exchPrfx')

                        prd_session = prd_tradeline[0].get('sessions').get('session')[0]
                        prd_session_id = prd_session.get('ids')
                        if(prd_session_id is not None):
                            #print(prd_session_id.get('ricRoot'))
                            
                            if(	'p_ricRoot'	in	columnList):contract_dict['p_ricRoot'] =prd_session_id.get('ricRoot')
                                                
                        
                        #contract_dict['p_tradeLine'] =row.get('tradeLines.tradeLine')
                        #contract_dict['p_underlier'] =row.get('underliers.underlier')
        
                        
                        c_basics = contract.get('basics')

                        if(	'c_name'	in	columnList):	contract_dict['c_name'] = c_basics.get('name')
                        if(	'c_assetTp'	in	columnList):	contract_dict['c_assetTp'] =c_basics.get('assetTp')
                        if(	'c_expDt'	in	columnList):	contract_dict['c_expDt'] =c_basics.get('expDt')
                        if(	'c_lstTrdDt'	in	columnList):	contract_dict['c_lstTrdDt'] =c_basics.get('lstTrdDt')
                        if(	'c_settleDt'	in	columnList):	contract_dict['c_settleDt'] =c_basics.get('settleDt')
                        if(	'c_frstDlvryDt'	in	columnList):	contract_dict['c_frstDlvryDt'] =c_basics.get('frstDlvryDt')
                        if(	'c_frstNtcDt'	in	columnList):	contract_dict['c_frstNtcDt'] =c_basics.get('frstNtcDt')
                        if(	'c_lstDlvryDt'	in	columnList):	contract_dict['c_lstDlvryDt'] =c_basics.get('lstDlvryDt')
                        if(	'c_name'	in	columnList):	contract_dict['c_name'] =c_basics.get('name')
                        if(	'c_vndrAssetTp'	in	columnList):	contract_dict['c_vndrAssetTp'] =c_basics.get('vndrAssetTp')
                        if(	'c_prntAssetTp'	in	columnList):	contract_dict['c_prntAssetTp'] =c_basics.get('prntAssetTp')
                        if(	'c_strikePx'	in	columnList):	contract_dict['c_strikePx'] =c_basics.get('strikePx')
                        if(	'c_cfi'	in	columnList):	contract_dict['c_cfi'] =c_basics.get('cfi')
                        if(	'c_yrCd'	in	columnList):	contract_dict['c_yrCd'] =c_basics.get('yrCd')
                        if(	'c_settleTp'	in	columnList):	contract_dict['c_settleTp'] =c_basics.get('settleTp')
                        if(	'c_ctrSz'	in	columnList):	contract_dict['c_ctrSz'] =c_basics.get('ctrSz')
                        if(	'c_frstTrdDt'	in	columnList):	contract_dict['c_frstTrdDt'] =c_basics.get('frstTrdDt')
                        if(	'c_settleFixDt'	in	columnList):	contract_dict['c_settleFixDt'] =c_basics.get('settleFixDt')
                        if(	'c_numOfLegs'	in	columnList):	contract_dict['c_numOfLegs'] =c_basics.get('numOfLegs')
                        if(	'c_accrlStrtDt'	in	columnList):	contract_dict['c_accrlStrtDt'] =c_basics.get('accrlStrtDt')
                        if(	'c_accrlEndDt'	in	columnList):	contract_dict['c_accrlEndDt'] =c_basics.get('accrlEndDt')
                        if(	'c_mnthCd'	in	columnList):	contract_dict['c_mnthCd'] =c_basics.get('mnthCd')
                        if(	'c_dayNum'	in	columnList):	contract_dict['c_dayNum'] =c_basics.get('dayNum')
                        if(	'c_pntVal'	in	columnList):	contract_dict['c_pntVal'] =c_basics.get('pntVal')
                        if(	'c_flexFl'	in	columnList):	contract_dict['c_flexFl'] =c_basics.get('flexFl')
                        if(	'c_actFl'	in	columnList):	contract_dict['c_actFl'] =c_basics.get('actFl')
                        if(	'c_wkNum'	in	columnList):	contract_dict['c_wkNum'] =c_basics.get('wkNum')
                        if(	'c_lstNtcDt'	in	columnList):	contract_dict['c_lstNtcDt'] =c_basics.get('lstNtcDt')
                        if(	'c_trdStsTp'	in	columnList):	contract_dict['c_trdStsTp'] =c_basics.get('trdStsTp')
                        if(	'c_cfiCd'	in	columnList):	contract_dict['c_cfiCd'] =c_basics.get('cfiCd')

                        
        
                        c_ids = contract.get('ids')

                        if(	'c_isin'	in	columnList):	contract_dict['c_isin'] =c_ids.get('isin')
                        if(	'c_bbgTicker'	in	columnList):	contract_dict['c_bbgTicker'] =c_ids.get('bbgTicker')
                        if(	'c_bbgIdBbUnique'	in	columnList):	contract_dict['c_bbgIdBbUnique'] =c_ids.get('bbgIdBbUnique')
                        if(	'c_aiiCode'	in	columnList):	contract_dict['c_aiiCode'] =c_ids.get('aiiCode')

                        prd_underlier = row.get('underliers.underlier')[0]
                        if(	'p_u_name'	in	columnList):	contract_dict['p_u_name'] =prd_underlier.get('basics').get('name')
                        if(	'p_u_ric'	in	columnList):	contract_dict['p_u_ric'] =prd_underlier.get('ids').get('ric')
                        if(	'p_u_ticker'	in	columnList):	contract_dict['p_u_ticker'] =prd_underlier.get('ids').get('ticker')
                        if(	'p_u_isin'	in	columnList):	contract_dict['p_u_isin'] =prd_underlier.get('ids').get('isin')
                        if(	'p_u_rduSecId'	in	columnList):	contract_dict['p_u_rduSecId'] =prd_underlier.get('ids').get('rduSecId')

        
        
                        
                        """contract_list.append(c_basics['name'])
                        rows_list = product_list + contract_list
                                                
                        data.loc[i] = rows_list
                        i = i+1
                        """
                        product_dict[input_key+"_"+ct_basics['exchCd']] = contract_dict
                
                if(fetchUnderlying):
                    #print(row)
                    underliers = row.get('underliers.underlier')
                    underlier = underliers[0]
                    underlyingIsin = underlier.get('ids').get('isin')
                    smic = underlier.get('basics').get('smic')
                    underlyingData = self.__get_underlying_data(underlyingIsin, smic)
                    if(not underlyingData['success'][0]):
                        #print('Tryig with omic')
                        omic = underlier.get('basics').get('omic')

                        underlyingData = self.__get_underlying_data(underlyingIsin, omic)
                   
                                                    
                    underlyingData = underlyingData.add_prefix('u_eq_')
                
        data = pd.DataFrame.from_dict(product_dict, orient='index')
        if(fetchUnderlying):
            series = underlyingData.iloc[0]
            for col in underlyingData:
                data[col] = series[col]
        return data
    
    """
    This method calls the resp api.
    """
    
    def __call_api(self, query, url):
        headers = {'x-api-key' : self.key,'accept':'application/json'}
        response = requests.get(url, params=query,headers=headers)
        data = response.text
        if not data:
            data = "{\"message\":\"No Data Found\"}"
        json_data = json.loads(data)
        return json_data
    
    def get_by_isin_with_underlier_data(self, isin, columnList=[]):
        """
        
        This will return the etd data given the isin
        Parameters
        ----------
        isin : String
            The ISIN code.
        columnList : List    
            Specify the list of column's that needs to be returned in output. 
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with isin "+isin)
        query = {'isin':isin}
        json_data = self.__call_api(query, 'https://sfbrekezl8.execute-api.eu-west-2.amazonaws.com/FreeTrial/etd/standard/getByIsin')
            
        data = self.__convert_json_to_df(isin,json_data,fetchUnderlying=True, columnList= columnList)
        columnList = []
        return data


    
    def get_by_isin(self, isin, columnList=[]):
        """
        
        This will return the etd data given the isin
        Parameters
        ----------
        isin : String
            The ISIN code.
        columnList : List    
            Specify the list of column's that needs to be returned in output. 
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with isin "+isin)
        query = {'isin':isin}
        json_data = self.__call_api(query, 'https://sfbrekezl8.execute-api.eu-west-2.amazonaws.com/FreeTrial/etd/standard/getByIsin')
            
        data = self.__convert_json_to_df(isin,json_data, fetchUnderlying=False, columnList=columnList)
        columnList = []
        return data


    def get_by_isins(self, isins = [], columnList=[]):
        """
        This will return the etd data given the isins
        Keyword Arguments:

        Parameters
        ----------
        isins : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.

        """
        data = []            
        for isin in isins:
            t_data = self.get_by_isin(isin,columnList)
            data.append(t_data)
        data = pd.concat(data)
        return data   

    def get_by_ticker_with_underlier_data(self, ticker, exchangeCode,columnList=[]):
        """
        This will return the etd data given the ticker and echange code
       

        Parameters
        ----------
        ticker : String
            Exchange symbol (also known as Ticker or Trade Symbol) of contract.
        exchangeCode : String
            Exchange code of the session where the security is trading.

        Returns
        -------
        data : dataframe
            This will return a dataframe with key as ticker+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.

        """
        print("Calling get_by_exchange_symbol with isin "+ticker+" exchangeCode-"+exchangeCode)
        query = {'ticker':ticker, 'exchangeCode':exchangeCode}
        json_data = self.__call_api(query, 'https://sfbrekezl8.execute-api.eu-west-2.amazonaws.com/FreeTrial/etd/standard/getByExchangeSymbol')
        data = self.__convert_json_to_df(ticker,json_data, fetchUnderlying=True)
       
        return data


    
    def get_by_ticker(self, ticker, exchangeCode,columnList=[]):
        """
        This will return the etd data given the ticker and echange code
       

        Parameters
        ----------
        ticker : String
            Exchange symbol (also known as Ticker or Trade Symbol) of contract.
        exchangeCode : String
            Exchange code of the session where the security is trading.

        Returns
        -------
        data : dataframe
            This will return a dataframe with key as ticker+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.

        """
        print("Calling get_by_exchange_symbol with isin "+ticker+" exchangeCode-"+exchangeCode)
        query = {'ticker':ticker, 'exchangeCode':exchangeCode}
        json_data = self.__call_api(query, 'https://sfbrekezl8.execute-api.eu-west-2.amazonaws.com/FreeTrial/etd/standard/getByExchangeSymbol')
        data = self.__convert_json_to_df(ticker,json_data, fetchUnderlying=False)
       
        return data
    
