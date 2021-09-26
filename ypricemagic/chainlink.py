from brownie import Contract
from cachetools.func import ttl_cache


feeds = {
    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": Contract("0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"),  # wbtc
    "0x514910771AF9Ca656af840dff83E8264EcF986CA": Contract("0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c"),  # link
    "0x584bC13c7D411c00c01A62e8019472dE68768430": Contract("0xBFC189aC214E6A4a35EBC281ad15669619b75534"),  # hegic
    "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9": Contract("0x547a514d5e3769680Ce22B2361c10Ea13619e8a9"),  # aave
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": Contract("0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"),  # weth
    "0xc00e94Cb662C3520282E6f5717214004A7f26888": Contract("0xdbd020CAeF83eFd542f4De03e3cF0C28A4428bd5"),  # comp
    "0xdB25f211AB05b1c97D595516F45794528a807ad8": Contract("0xb49f677943BC038e9857d61E7d053CaA2C1734C1"),  # eurs
    "0xC581b735A1688071A1746c968e0798D642EDE491": Contract("0xb49f677943BC038e9857d61E7d053CaA2C1734C1"),  # eurt
    "0xD71eCFF9342A5Ced620049e616c5035F1dB98620": Contract("0xb49f677943BC038e9857d61E7d053CaA2C1734C1"),  # seur
    "0x5555f75e3d5278082200Fb451D1b6bA946D8e13b": Contract("0xBcE206caE7f0ec07b545EddE332A47C2F75bbeb3"),  # ibjpy
    "0xFAFdF0C4c1CB09d430Bf88c75D88BB46DAe09967": Contract("0x77F9710E7d0A19669A13c055F62cd80d313dF022"),  # ibaud
    "0x69681f8fde45345C3870BCD5eaf4A05a60E7D227": Contract("0x5c0Ab2d9b5a7ed9f470386e82BB36A3613cDd4b5"),  # ibgbp
    "0x1CC481cE2BD2EC7Bf67d1Be64d4878b16078F309": Contract("0x449d117117838fFA61263B61dA6301AA2a88B13A"),  # ibchf
    "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e": Contract("0xA027702dbb89fbd58938e4324ac03B58d812b0E1"),  # yfi
    # NOTE: These coins don't have oracles but we can use the oracle for the base token
    "0x9AFb950948c2370975fb91a441F36FDC02737cD4": Contract("0x1A31D42149e82Eb99777f903C08A2E41A00085d3"),  # hfil
    "0x5CAF29fD8efbe4ED0cfc43A8a211B276E9889583": Contract("0x1A31D42149e82Eb99777f903C08A2E41A00085d3"),  # renfil
    "0x95dFDC8161832e4fF7816aC4B6367CE201538253": Contract("0x01435677fb11763550905594a16b645847c1d0f3"),  # ibKRW
    "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6": Contract("0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"),  # sbtc
    "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D": Contract("0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"),  # renbtc
}


@ttl_cache(ttl=600)
def get_price(asset, block=None):
    try:
        return feeds[asset].latestAnswer(block_identifier=block) / 1e8
    except (KeyError, ValueError):
        return None
