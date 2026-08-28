Full sales : from 2023 to 2025

        Data columns (total 8 columns):
        #   Column      Non-Null Count  Dtype  
        ---  ------      --------------  -----  
        0   OrderID     4456 non-null   object 
        1   CustomerID  4432 non-null   object 
        2   ProductID   4456 non-null   int64  
        3   OrderDate   4456 non-null   object 
        4   Quantity    4456 non-null   int64  
        5   Revenue     4415 non-null   float64
        6   COGS        4456 non-null   float64


sample :
            OrderID	                                         CustomerID	             ProductID	OrderDate	Quantity	Revenue	COGS	
    0	53a9ac5e-e0df-491b-af5a-171c8e3ea288	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	1016	2023-01-11	1	43.20	28.28
    1	129d9c61-160a-4253-9e87-4a1626963ef1	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	1010	2023-12-08	2	210.46	135.90
    2	0fe79c57-f7e4-40a2-9970-44fb7cbf8188	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	1040	2023-11-06	2	48.26	16.90
    3	16d96526-e2e7-4484-9b1d-f9a80431bce8	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	1015	2023-02-02	4	96.52	33.80
    4	52dfee96-beed-4ac6-935a-81aaa1ccb578	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	1020	2023-06-06	1	27.37	21.90

products:

        #   Column           Non-Null Count  Dtype  
        ---  ------           --------------  -----  
        0   ProductID        50 non-null     int64  
        1   ProductName      50 non-null     object 
        2   ProductCategory  50 non-null     object 
        3   Price            50 non-null     float64
        4   Base_Cost        50 non-null     float64 

sample :
    
    ProductID	ProductName	                   ProductCategory	 Price   Base_Cost
    0	1001	Single-Origin Ethiopian (250g)	Consumables	    19.49	11.55
    1	1002	Seasonal Blend Light Roast	    Consumables	    35.53	5.39
    2	1003	Decaf Blend (1kg)	            Consumables	    40.35	11.69
    3	1004	Cold Brew Concentrate	        Consumables	    23.49	9.17
    4	1005	Espresso Bean Sampler Pack	    Consumables	    19.06	10.88


customers:

        #   Column            Non-Null Count  Dtype 
        ---  ------            --------------  ----- 
        0   CustomerID        200 non-null    object
        1   Region            200 non-null    object
        2   CustomerJoinDate  200 non-null    object

sample :
              CustomerID	                       Region CustomerJoinDate
        0	345e77bf-4a44-4a4c-9b4f-6f5e21e39e8b	East	2023-08-03
        1	c672d9cb-b74b-48ea-bff3-908ff9790632	West	2023-03-13
        2	19ebe822-7b55-4146-9fbf-7f30a95fcc27	West	2023-09-08
        3	8553b15d-bab5-41e2-b9b1-3bd3e2a7c51e	West	2023-04-17
        4	2de84462-b349-47ab-8700-7ac254586db9	West	2023-01-23
