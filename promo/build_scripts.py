"""Builds promo/scripts.json: one short video per day, Nov 16 2026 - Apr 15 2027.
Every claim matches the website's IRS-sourced facts. Edit TOPICS and re-run to change content."""
import json, datetime as dt
D={'doordash':('DoorDash','DoorDash drivers','#doordash #dasher #doordashdriver'),
   'uber':('Uber','Uber drivers','#uberdriver #rideshare #ubereats'),
   'lyft':('Lyft','Lyft drivers','#lyftdriver #rideshare'),
   'instacart':('Instacart','Instacart shoppers','#instacart #instacartshopper'),
   'flex':('Amazon Flex','Amazon Flex drivers','#amazonflex #amazonflexdriver')}
ALL=list(D)
# scene: (type, on-screen text, small text, image, voice line). type: title | screen
T=lambda *a:a
TOPICS={
'A':[ # Nov 16 - Dec 31: habits and planning
 dict(id='setaside',drivers=ALL,hook='{who}: how much should you save for taxes this week?',scenes=[
  T('title','{who}:','how much should you save for taxes this week?',None,'{who}, how much should you save for taxes this week?'),
  T('screen','No one takes tax out of your pay','','home','{app} does not take any tax out of your pay. So you need your own number.'),
  T('screen','One number, every week','Uses 2026 IRS brackets','home','Gig Tax Buddy gives you one number every week, using the twenty twenty six I.R.S. brackets.')]),
 dict(id='setax',drivers=ALL,hook='The 15.3% tax most new {who} miss',scenes=[
  T('title','The 15.3% surprise','most new {who} miss',None,'Here is the tax most new {who} miss.'),
  T('screen','Self-employment tax','15.3% on most of your profit','receipt','Self employment tax is fifteen point three percent on most of your profit, on top of income tax.'),
  T('screen','Save for it weekly','','home','Put a little aside every week, and April is never a surprise.')]),
 dict(id='mileage',drivers=ALL,hook='Every mile you drive is worth 72.5 cents at tax time',scenes=[
  T('title','72.5¢','every business mile in 2026',None,'Every business mile you drive is worth seventy two and a half cents at tax time.'),
  T('screen','400 miles a week','= $13,920 deduction a year','receipt','Four hundred miles a week adds up to a deduction of almost fourteen thousand dollars a year.'),
  T('screen','Log it in a minute','Odometer or your mileage app','log','Log your miles once a week, from your odometer or your mileage app.')]),
 dict(id='tips',drivers=ALL,hook='{who}: your tips can now lower your income tax',scenes=[
  T('title','No tax on tips','for {who}, 2025 to 2028',None,'{who}, your tips can now lower your income tax.'),
  T('screen','Up to $25,000 a year','Income tax, not self-employment tax','ded','Delivery and rideshare drivers can deduct qualified tips, up to twenty five thousand dollars a year.'),
  T('screen','Track tips separately','','log','But only if you track them. Log your tips separately, and the app applies the deduction.')]),
 dict(id='hourly',drivers=ALL,hook='What do you really make per hour on {app}?',scenes=[
  T('title','Your real hourly pay','after car costs',None,'What do you really make per hour on {app}?'),
  T('screen','Subtract the car','72.5¢ a mile','home','Take out the cost of your car at seventy two and a half cents a mile.'),
  T('screen','See it every week','','home','Gig Tax Buddy shows your real hourly pay every week. It is often an eye opener.')]),
 dict(id='w4',drivers=ALL,hook='Have a day job? You may never need quarterly payments',scenes=[
  T('title','Have a day job?','Skip quarterly payments',None,'Driving for {app} on top of a day job? You may not need quarterly payments.'),
  T('screen','One W-4 change','Step 4(c): extra withholding','w4','Add extra withholding on a new W-4 at your job. The app gives you the exact amount.'),
  T('screen','Counts all year','IRS Form 2210 rule','w4','The I.R.S. counts paycheck withholding as paid evenly through the year, so it can catch up earlier quarters.')]),
 dict(id='q4prep',drivers=ALL,hook='{who}: your next IRS payment is due January 15',scenes=[
  T('title','January 15','next IRS payment',None,'{who}, your next estimated tax payment is due January fifteenth.'),
  T('screen','Know the amount','Safe harbor plan','irs','The planner shows how much to pay to stay penalty free.'),
  T('screen','Pay free at IRS.gov','Direct Pay','irs','Pay for free at I.R.S. dot gov, with Direct Pay.')]),
 dict(id='doubledip',drivers=ALL,hook="Don't deduct gas if you use the mileage rate",scenes=[
  T('title',"Don't double-dip",'gas is already in the mileage rate',None,'Using the mileage rate? Then do not deduct gas too.'),
  T('screen','Already included','Gas, repairs, insurance, car washes','ded','Gas, oil changes, repairs and insurance are already inside the seventy two and a half cent rate.'),
  T('screen','What you CAN add','Tolls, parking, phone, supplies','ded','You can add tolls, parking, your phone and supplies on top.')]),
 dict(id='phone',drivers=ALL,hook='Your phone bill is partly tax-deductible',scenes=[
  T('title','Your phone bill','is partly deductible',None,'{who}, part of your phone bill is a business expense.'),
  T('screen','Business share','e.g. 60% of $75 a month','ded','If you use your phone sixty percent for gig work, that share can be deducted.'),
  T('screen','Find every deduction','','ded','The deduction finder adds it up for you.')]),
 dict(id='weekly',drivers=ALL,hook='Track your gig taxes in one minute a week',scenes=[
  T('title','One minute a week','that is all it takes',None,'Tracking gig taxes takes about one minute a week.'),
  T('screen','Type each app total','Tips and miles too','log','Type what each app paid you, your tips and your miles.'),
  T('screen','Get your number','','home','Then you get your set aside number for the week.')]),
 dict(id='install',drivers=ALL,hook='A free tax app for {who}. No account needed.',scenes=[
  T('title','Free for {who}','no account, no app store',None,'Here is a free tax tool for {who}. No account needed.'),
  T('screen','Try the calculator','Right in your browser','receipt','Open the link, try the calculator, and see your weekly number.'),
  T('screen','Add to home screen','Works offline','home','Then add it to your home screen. It works like an app, even offline.')]),
 dict(id='proof',drivers=ALL,hook='Keep proof of your miles the IRS can trust',scenes=[
  T('title','Proof of your miles','made at the time',None,'The I.R.S. expects a mileage record made at the time.'),
  T('screen','Odometer readings','Plus optional photos','miles','Log your odometer, and snap a photo if you want proof.'),
  T('screen','Export for tax time','','miles','At tax time, export one report for your preparer.')]),
],
'B':[ # Jan 1 - Jan 15
 dict(id='q4due',drivers=ALL,hook='Q4 estimated tax is due January 15',scenes=[
  T('title','Due January 15','fourth quarter estimated tax',None,'{who}, fourth quarter estimated tax is due January fifteenth.'),
  T('screen','How much to pay','','irs','Check how much to pay so you stay penalty free.'),
  T('screen','Pay at IRS.gov','Direct Pay is free','irs','Then pay for free at I.R.S. dot gov.')]),
 dict(id='safeharbor',drivers=ALL,hook='The IRS safe harbor rule every driver should know',scenes=[
  T('title','The safe harbor rule','avoid the penalty',None,'Here is the I.R.S. rule that helps you avoid the underpayment penalty.'),
  T('screen','Pay 90% of this year','or 100% of last year','irs','Pay at least ninety percent of this year\'s tax, or one hundred percent of last year\'s. One hundred ten percent above a hundred fifty thousand.'),
  T('screen','Your plan, done for you','','irs','The quarterly planner works it out for you.')]),
],
'C':[ # Jan 16 - Feb 28: forms
 dict(id='1099k',drivers=['uber','lyft'],hook='Why your {app} 1099-K shows more than you were paid',scenes=[
  T('title','Your 1099-K looks too high?','here is why',None,'Does your {app} 1099-K show more than you were paid?'),
  T('screen','Gross, before fees','Deduct the fees','f1099','The 1099-K shows the gross amount, before fees. Report it, and deduct the fees.'),
  T('screen','Check it in 2 minutes','','f1099','Skip the fees and you pay tax on money you never got. The 1099 checker shows the difference.')]),
 dict(id='1099nec',drivers=['uber','lyft','doordash','instacart','flex'],hook='Got a 1099-NEC from {app}? Here is what it means',scenes=[
  T('title','Got a 1099-NEC?','here is what it means',None,'Got a 1099-NEC from {app}? Here is what it means.'),
  T('screen','It reports your pay','All gig income is taxable','f1099','It reports what the app paid you. Match it to your own records.'),
  T('screen','Match your records','','f1099','The 1099 checker flags it when your log and your form do not match.')]),
 dict(id='noform',drivers=ALL,hook='No 1099 from {app}? You still owe tax.',scenes=[
  T('title','No 1099?','you still owe tax',None,'Did not get a 1099 from {app}? The income is still taxable.'),
  T('screen','All gig income counts','Form or no form','receipt','All gig income counts, whether or not a form arrives.'),
  T('screen','Your records are proof','','miles','Your own log of earnings and miles is what you file from.')]),
 dict(id='export',drivers=ALL,hook='Hand your preparer everything in one file',scenes=[
  T('title','Tax time, sorted','one file for your preparer',None,'Make tax time easy, with one file for your tax preparer.'),
  T('screen','Every shift and mile','Plus your profit estimate','miles','Every shift, every mile and your profit estimate, in one export.'),
  T('screen','Ready in one tap','','miles','Ready in one tap.')]),
],
'D':[ # Mar 1 - Apr 15
 dict(id='april',drivers=ALL,hook='{who}: April 15 is coming. Are your numbers ready?',scenes=[
  T('title','April 15','is coming',None,'{who}, April fifteenth is coming. Are your numbers ready?'),
  T('screen','Profit, miles, tips','All in one place','miles','Your profit, miles and tips, all in one place.'),
  T('screen','Do not leave money behind','','ded','Check every deduction before you file.')]),
 dict(id='tipsfile',drivers=ALL,hook='Filing this year? Do not forget the tips deduction',scenes=[
  T('title','Filing soon?','claim the tips deduction',None,'Filing soon? Do not forget the new tips deduction.'),
  T('screen','Drivers qualify','Occupations 802 and 804','ded','Rideshare and delivery drivers are on the Treasury list of tipped occupations.'),
  T('screen','Up to $25,000','','ded','It can take up to twenty five thousand dollars of tips off your income tax.')]),
 dict(id='qbi',drivers=ALL,hook='The 20% deduction many drivers have never heard of',scenes=[
  T('title','The 20% deduction','on your gig profit',None,'Here is a deduction many drivers have never heard of.'),
  T('screen','Business income deduction','Now permanent','ded','The qualified business income deduction can lower income tax on twenty percent of your profit.'),
  T('screen','Applied for you','','home','Gig Tax Buddy includes it in your weekly number.')]),
 dict(id='bothapps',drivers=ALL,hook='Keep your mileage app. Add the tax side.',scenes=[
  T('title','Keep your mileage app','add the tax side',None,'Keep your free mileage app. Add the tax side.'),
  T('screen','Type its weekly miles','','log','Type in its weekly miles, and your earnings.'),
  T('screen','Know what you owe','','home','Then you know exactly what to save, and when to pay.')]),
]}
TOPICS['C']+=[TOPICS['A'][i] for i in (2,3,4,5)]
TOPICS['D']+=TOPICS['A'][:4]
def season(d):
    if d<dt.date(2027,1,1): return 'A'
    if d<=dt.date(2027,1,15): return 'B'
    if d<dt.date(2027,3,1): return 'C'
    return 'D'
out=[];d=dt.date(2026,11,16);k={s:0 for s in 'ABCD'};dk=0
while d<=dt.date(2027,4,15):
    s=season(d);t=TOPICS[s][k[s]%len(TOPICS[s])];k[s]+=1
    drv=t['drivers'][dk%len(t['drivers'])];dk+=1
    app,who,tags=D[drv];f=lambda x:x.replace('{who}',who).replace('{app}',app)
    hook=f(t['hook']);hook=hook[0].upper()+hook[1:]
    out.append(dict(date=d.isoformat(),id=f"{d.isoformat()}-{t['id']}-{drv}",topic=t['id'],driver=drv,title=hook,
      scenes=[dict(type=a,text=f(b),sub=f(c),img=e,vo=f(v)) for a,b,c,e,v in t['scenes']],
      caption=f"{hook}\n\nFree tax calculator for gig drivers: link in profile. No account needed.\nEstimates, not tax advice. Voiceover is AI-generated.\n\n{tags} #gigtaxes #1099 #selfemployed #taxtips"))
    d+=dt.timedelta(days=1)
json.dump(out,open(__file__.replace('build_scripts.py','scripts.json'),'w'),indent=1)
print(len(out),'scripts',out[0]['date'],'->',out[-1]['date'])
