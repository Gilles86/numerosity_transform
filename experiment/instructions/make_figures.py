import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
OUT="/Users/gdehol/git/numerosity_transform/experiment/instructions/"
N=list(range(6,51,2))
M={"linear":[float(n) for n in N],
"concave":[6.0,11.5,16.5,21.0,24.5,28.0,31.0,33.5,36.0,38.0,39.5,41.5,42.5,44.0,45.0,46.0,46.5,47.5,48.0,48.5,49.0,49.5,50.0],
"convex":[6.0,6.5,7.0,7.5,8.0,8.5,9.5,10.0,11.0,12.0,13.5,14.5,16.5,18.0,20.0,22.5,25.0,28.0,31.5,35.0,39.5,44.5,50.0]}
assert all(len(v)==23 for v in M.values())

def cloud(n,seed,path,center_text=None):
    rng=np.random.default_rng(seed); R=1.0; r=0.055; pts=[]
    hole=0.17 if center_text else 0
    while len(pts)<n:
        a=rng.uniform(0,2*np.pi); d=(R-r)*np.sqrt(rng.uniform(0,1))
        p=np.array([d*np.cos(a),d*np.sin(a)])
        if d<hole+r: continue
        if all(np.hypot(*(p-q))>2.4*r for q in pts): pts.append(p)
    fig,ax=plt.subplots(figsize=(2.6,2.6),facecolor="black")
    ax.add_patch(Circle((0,0),R,color="#222222"))
    for p in pts: ax.add_patch(Circle(p,r,color="white"))
    if center_text: ax.text(0,0,center_text,color="#2ecc40",ha="center",va="center",fontsize=16,fontweight="bold")
    ax.set_xlim(-1.05,1.05);ax.set_ylim(-1.05,1.05);ax.set_aspect("equal");ax.axis("off")
    fig.savefig(path,dpi=200,facecolor="black",bbox_inches="tight",pad_inches=0.02);plt.close(fig)

def fmt(v): return f"{v:g}"

DESC={
"linear":"The relationship is linear: the value of a dot cloud (in CHF) is simply equal to its number of dots. Each additional dot adds the same amount of money, wherever you are on the scale -- for example, a cloud with 20 dots is worth 20 CHF and a cloud with 40 dots is worth 40 CHF. So, this is what you are supposed to learn.",
"concave":"As you can see, the relationship between the number of dots and the value is not linear: the value rises steeply for small numbers of dots and then flattens out for large numbers of dots. For example, going from 6 to 12 dots increases the value by 15 CHF (from 6 to 21 CHF), whereas going from 38 to 44 dots increases the value by only 2 CHF (from 46.5 to 48.5 CHF). So, this is what you are supposed to learn.",
"convex":"As you can see, the relationship between the number of dots and the value is not linear: the value rises only slowly for small numbers of dots and then increases steeply for large numbers of dots. For example, going from 6 to 12 dots increases the value by only 1.5 CHF (from 6 to 7.5 CHF), whereas going from 38 to 44 dots increases the value by 10 CHF (from 25 to 35 CHF). So, this is what you are supposed to learn."}
EXN={"linear":30,"concave":30,"convex":30}
TEMPLATE=open(OUT+"../../.tmpl.md").read() if False else None

T = r'''# Instructions (mapping @NAME@)

Welcome to this study! And thank you for participating.

Please carefully read the material on the following pages to understand:

- The task you will complete today.

- The rules of how you will be paid out.

Your task today will be to learn the relation between the number of dots
in a cloud of dots (Figure 1 shows you an example) and its monetary
value. Each dot cloud has a specific monetary value assigned to it
according to its number of dots (like a bank note). The number of dots
ranges from 6 to 50, in steps of 2, so there are 23 different dot
clouds. To learn the relation, you will first be shown all possible dot
clouds together with their corresponding monetary value (Phase 1). After
that you will be shown a random dot cloud and you need to input the
monetary amount that matches its value. You will get feedback on this
(Phase 2). Finally, you will again be shown a dot cloud and can bid
money to purchase it. Later, you can sell it for its actual monetary
value that you learned in the previous phase (Phase 3). Since your bid
is the maximum price you will have to pay to buy the dot cloud (the
price is randomly determined, up to your bid), you are best off to bid
the real monetary value of the dot cloud. In this phase, there is no
feedback. So, in the end, you will be paid according to how well you
learned the relationship between the number of dots and their values in
phase 2, and according to the difference between the random price set by
the computer if you won the bid and the resell value of the dot clouds
you purchased in phase 3.

![](@FIG1@){width=1.8in}

*Figure 1: Example of a dot cloud (here: 24 dots).* [Figure: example dot cloud with 24 dots]

**Note:** you will not have time to count the dots one by one. Use your
impression of how many dots there are. @TODO_NOTE@

We will now explain each phase in detail. After this, **there will be a
few test questions** to make sure you properly understand the experiment
and the payout scheme.

By agreeing to participate, you have already earned a show-up fee of
@SHOWUP@ CHF. It is **very** important that you understand the following
instructions, since the additional payoffs from participating in the
experiment will depend on your ability to make good decisions. Thank you
again for participating in this experiment!

## Experiment Description

## [First phase of the experiment]{.underline}

**In the first phase of the experiment, you learn the monetary value of
the different dot clouds. You are shown all possible dot clouds together
with their corresponding monetary values in the middle (see Figure 2).**
You can look at the dot clouds and their numerical values for as long as
you want and proceed by pressing ENTER. If you want to see past dot
clouds again, you can go back by pressing BACKSPACE. @TODO_KEYS@

![](@FIG2@){width=1.8in}

*Figure 2: Example of one dot cloud (@EX@ dots) together with its
corresponding correct value (@EXV@ CHF) in the middle.* [Figure: example dot cloud with @EX@ dots]

The values of the dot clouds range between 6 and 50. The value is a
function of the number of dots. The exact function is shown in Figure 3.
@DESC@

![](@FIG3@){width=4.2in}

*Figure 3: Mapping function from the number of dots to its value
(@NAME@ mapping).*

Pay close attention during this phase of the experiment already. You
need to learn this exact relationship to earn the maximum money
possible.

## [Second phase of the experiment]{.underline}

**In the second phase of the experiment, you will be shown a dot cloud
and have to input its associated monetary value.** The dot cloud will be
shown in the center of your screen for a short moment (**TODO(Gilles)**:
presentation duration), after which a response slider appears (see
Figure 4).

[Figure: example training trial -- dot cloud, response slider, and feedback; **TODO(Gilles)**: add screenshot of the numerosity version]

*Figure 4: Example of one training trial with negative feedback, where
the actual value is @EXV@ and the input was 3.5.*

For each round, your task is to input a monetary value so that it
matches the value of the number of dots of the dot cloud that you
learned in phase 1. Move the slider to the value you believe corresponds
to the dot cloud and **click to confirm**. **TODO(Gilles)**: confirm
response method (slider + click as in abstract_values v5, vs. typing the
number as in the old booklets). If your input matches the monetary value
of the dot cloud exactly, you will be shown green feedback. If the value
does not match the monetary value of the dot cloud, you will be shown
red feedback. In the lower half of your screen, you will be given the
actual value of the dot cloud. For every dot cloud, you should ask
yourself: **What is the monetary value of this dot cloud? That is, how
much money would I get if I sold this dot cloud?** You have @TLIM2@
seconds to make a guess. In total, you will complete @N2@ rounds in this
phase of the experiment for 23 different dot clouds. This means that you
will see every dot cloud @REP@ times. The sequence of dot clouds is
completely random.

Try to predict the monetary value of the dot clouds in this phase as
accurately as possible. **Your payment will depend on how well you have
learned this relationship.** You will earn more if you are able to guess
the associated value of the dot cloud with the **least possible
difference to the true value in each guess**.

**Note:** You will have the opportunity to take short breaks between
blocks. Use this time to rest if needed, but remember that your
performance -- and thus your earnings -- will depend on your focus and
accuracy.

## [Third and final phase of the experiment]{.underline}

**In the third and final phase of the experiment, you have to input the
monetary value of a presented dot cloud as a BID in an AUCTION (see
Figure 5).** The difference to the previous phase is that you will not
receive feedback and that you only have a very limited amount of time to
input a value (@TLIM3@ seconds). The value of the dot cloud is exactly
what you learnt in the first two phases of the experiment.

Your budget for each trial is 50 CHF. You will keep the rest of the
budget after paying the price of the dot cloud if you win the bidding.
The dot clouds you bought will be exchanged for money at the end of the
experiment, and you will get @FRAC@ of the money you win here as extra
payment. As you will see in a moment, your best strategy is to bid your
true value for the dot cloud.

[Figure: example phase 3 trial -- dot cloud and response slider, no feedback; **TODO(Gilles)**: add screenshot]

*Figure 5: Example of one phase 3 trial (final phase) in which you have
to input the value of the dot cloud without feedback.*

You can submit your value by confirming your response (**click the mouse
button** / press ENTER -- **TODO(Gilles)**: confirm). **If you do not
confirm, your input will not be registered and you will not get any
payout for this trial!** You only have a limited time of @TLIM3@ seconds
to input your value. To maximize your payment, you should always make a
choice within the given timeframe. At the beginning of this phase you
have the opportunity to test a trial two times before the actual trials
start.

In every auction there is a rule that determines the price at which the
items are sold. This auction is no different.

The rule for our auction is a bit unusual, but its implications are
straightforward: There is no way of gaming the auction, the BEST thing
that you can do in every trial is to ask yourself how much you would be
willing to pay to get THAT dot cloud and then bid the number closest to
that value.

What is the rule? At the end of each trial, the computer will choose a
random price for the dot cloud which will range between 6 and 50 (the
range of possible values of the dot clouds). If your bid is greater than
the random price, you will get the dot cloud for the random price. You
can then sell it in the end for its true value and earn the difference
between the true value and the random price you paid for it. If your bid
is less or equal than the random value, you will NOT get the dot cloud
but will not have to pay any money and won't earn any additional money
from this trial.

Why is it in your interest to bid the value closest to your true value
for the dot cloud?

You might think that your best strategy is to bid less than the dot
cloud is worth to you. This is INCORRECT. The payout you get is
determined by the random price that the computer draws (your earnings
are the difference between the true value of the dot cloud and the
random price you paid) and NOT by your bid. Thus, if you lower your bid
you would not be able to affect the payout, but might end up losing the
opportunity to get the dot cloud at a "good" price (and therefore not
earn any additional payout).

For example, suppose that the dot cloud is worth 20 CHF to you. If you
bid your true value, you will get the dot cloud if the random value is
anything between 6 and 20 CHF. You will not get the dot cloud if the
random value is 20 CHF or above. It follows that by bidding your true
value you make a "profit" since you always end up paying less than the
dot cloud is worth to you.

Clearly, you should never bid more than your true value. (If you bid
more than your true value and you win the bid for a price higher than
the true value, your payout will be negative.)

What happens if you bid less than you true value? For example, suppose
that you bid 6 CHF even though your true value is 20 CHF. In this case
you never get the dot cloud, which is not a good strategy since, when
you bid your true value, you pretty much always end up paying less than
the dot cloud is worth to you!

Note another attractive property of the auction rules: conditional on
getting the dot cloud (i.e, conditional on the random number being less
or equal to your bid), the price that you pay is on average half of your
bid.

Thus, if you follow your best strategy and always bid the true value, on
a typical trial you will get to buy the dot cloud at approximately half
its true value (and thus earn half its value as the corresponding
payout)!

Don't let the details of the experiment confuse you, phase 3 trials are
actually very simple:

1.  You will make bids for purchasing a dot cloud on @N3@ trials.

2.  You should treat each decision as if it were the only one.

3.  Your best strategy is to always bid the number closest to your true
    value for getting that dot cloud at the end of the experiment.

4.  If you follow the best strategy, on average the price that you pay
    for a dot cloud will be half of the value you bid.

5.  In the end, you will get @FRAC@ of the total money you accumulated
    during the trials you participated in during this phase as real
    money. (Remember: If you do not submit a bid during a trial, this
    trial does not count as a trial that you participated in!)

6.  Your average payout in the task will be around @AVG@ CHF.
'''
TD=lambda s: f"**TODO(Gilles)**: {s}"
for name,vals in M.items():
    f1=f"dotcloud_example_24.png"
    cloud(24,1,OUT+f1)
    ex=30; exv=vals[N.index(ex)]
    f2=f"dotcloud_example_{name}.png"; cloud(ex,2,OUT+f2,fmt(exv))
    f3=f"mapping_{name}.png"
    fig,ax=plt.subplots(figsize=(5,3.6))
    ax.plot(N,vals,"-o",color="#1f77b4",ms=4)
    ax.set_xlabel("Number of dots"); ax.set_ylabel("Value (CHF)")
    ax.set_xlim(4,52); ax.set_ylim(4,52); ax.set_xticks(range(6,51,8)); ax.set_yticks(range(10,51,10))
    ax.set_title(f"{name.capitalize()} mapping"); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT+f3,dpi=200); plt.close(fig)
    t=T
    rep={"NAME":name.upper(),"FIG1":f1,"FIG2":f2,"FIG3":f3,"EX":str(ex),"EXV":fmt(exv),"DESC":DESC[name],
     "SHOWUP":TD("show-up fee")[:0]+"**TODO(Gilles)**","TLIM2":"**TODO(Gilles)**","N2":"**TODO(Gilles)** (230?)","REP":"**TODO(Gilles)** (10?)",
     "TLIM3":"**TODO(Gilles)**","FRAC":"**TODO(Gilles)** (payout fraction)","N3":"**TODO(Gilles)**","AVG":"**TODO(Gilles)**",
     "TODO_NOTE":"**TODO(Gilles)**: confirm presentation duration and whether this note should be shown to participants.",
     "TODO_KEYS":"**TODO(Gilles)**: confirm keys for the numerosity version (old: ENTER / BACKSPACE; v5: RIGHT / LEFT ARROW, SPACE BAR to continue)."}
    for k,v in rep.items(): t=t.replace(f"@{k}@",v)
    assert "@" not in t.replace("@@","")
    open(OUT+f"instructions_{name}.md","w").write(t)
