import chainladder as cl

raa = cl.load_sample("RAA")
raa_1989 = raa[raa.valuation < raa.valuation_date]
cl_ult = cl.Chainladder().fit(raa).ultimate_  # Chainladder Ultimate
apriori = cl_ult * 0 + (float(cl_ult.sum()) / 10)  # Mean Chainladder Ultimate
apriori_1989 = apriori[apriori.origin < "1990"]


def test_cc_predict():
    cc = cl.CapeCod().fit(raa_1989, sample_weight=apriori_1989)
    cc.predict(raa, sample_weight=apriori)


def test_bf_predict():
    cc = cl.BornhuetterFerguson().fit(raa_1989, sample_weight=apriori_1989)
    cc.predict(raa, sample_weight=apriori)


def test_mack_predict():
    mack = cl.MackChainladder().fit(raa_1989)
    mack.predict(raa_1989)
    # mack.predict(raa)


def test_bs_random_state_predict():
    tri = (
        cl.load_sample("clrd")
        .groupby("LOB")
        .sum()
        .loc["wkcomp", ["CumPaidLoss", "EarnedPremNet"]]
    )
    X = cl.BootstrapODPSample(random_state=100).fit_transform(tri["CumPaidLoss"])
    bf = cl.BornhuetterFerguson(apriori=0.6, apriori_sigma=0.1, random_state=42).fit(
        X, sample_weight=tri["EarnedPremNet"].latest_diagonal
    )
    assert (
        abs(
            bf.predict(X, sample_weight=tri["EarnedPremNet"].latest_diagonal)
            .ibnr_.sum()
            .sum()
            / bf.ibnr_.sum().sum()
            - 1
        )
        < 5e-3
    )


def test_basic_transform():
    tri = cl.load_sample("raa")
    cl.Development().fit_transform(tri)
    cl.ClarkLDF().fit_transform(tri)
    cl.TailClark().fit_transform(tri)
    cl.TailBondy().fit_transform(tri)
    cl.TailConstant().fit_transform(tri)
    cl.TailCurve().fit_transform(tri)
    cl.BootstrapODPSample().fit_transform(tri)
    cl.IncrementalAdditive().fit_transform(tri, sample_weight=tri.latest_diagonal)
