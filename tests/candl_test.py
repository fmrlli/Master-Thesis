import candl
import spt_candl_data
import candl_data
import clipy

# Likelihoods
like1 = candl.Like(spt_candl_data.SPT3G_D1_TE)
like2018 = candl.Like(candl_data.SPT3G_2018_TTTEEE)

print(like1, like2018)
