
t1 = Token(27, 72, 'YUJM3429', None, None, '2017-03-1 12:10:00',None )
t2 = Token(35, 53, 'EBFJ7563', None, None, '2017-03-1 13:25:00',None )

c1 = Charge(72, 1, '345.838041336,136.760215927,117.756374002,154.316951328,407.285097246,314.584206789,336.853522898,160.158070963,373.613117668,315.968793367,425.73476295,419.912814111,141.468511831,414.808583565,378.19519791,294.694347344,466.630655317,191.837441757,212.53113923,395.156939957,450.965877768,230.298492369,203.046643736,418.810565928#307.353519451,115.211695918,234.1890198,254.428928201,339.447108293,409.65540967,253.361187448,482.536364812,267.577897324,199.273359508,269.989091726,374.70837994,364.456843087,116.518588443,361.397846293,144.861181161,152.117950889,243.504648953,477.242402057,356.408591437,167.794431912,484.743430945,216.034803502,212.359843092#387.858959358,433.959131403,313.931934302,129.774483807,173.073702442,463.055360316,111.06281328,304.04130892,300.532446318,321.903942626,348.537413817,358.093056565,466.062642192,338.469511165,228.590034231,444.513872908,380.305942693,495.45461176,385.044485734,408.615316988,168.056782881,242.274799879,257.564460614,498.382650178#268.215157446,247.576657125,255.964018977,183.976617173,198.263757663,237.900013299,110.923826079,166.830865785,344.716880815,267.605813127,234.158403587,173.824908383,411.090717926,419.634802545,279.207506694,349.812770992,152.674185001,257.644649493,235.084038635,462.927759253,379.667326104,338.436326107,308.039294864,277.267723815#148.768618357,210.792709025,487.513866666,376.933559159,334.364162049,245.075880751,102.661759307,279.864162768,272.063266744,265.877329571,436.179642092,407.489716403,360.112408057,255.496260058,452.279040533,373.271931225,282.712069062,168.305671228,304.314637794,281.885136663,266.198887009,408.007174904,283.744646707,415.613433224#479.425478321,430.79902197,277.275829219,398.132319481,272.542163397,132.192295239,339.641466942,158.179613762,189.592058999,491.099777844,174.352658787,471.772472701,289.735495716,223.016137011,109.290382772,169.814843093,465.467347417,431.010739588,336.169523876,197.665983714,136.243071743,185.314475989,109.694167256,149.541461923#195.33022075,227.886554829,466.346339439,178.420776401,347.121528113,433.444832395,245.577099801,262.248455404,213.376604424,433.171086,171.414570622,240.100182094,366.859811937,402.621891226,177.308699868,235.871726077,244.48382738,323.854550624,329.195845738,108.652717127,499.726558665,465.827227145,256.853840296,234.710079913', True, '2017-03-1 10:10:00')

db.session.add(t1)
db.session.add(t2)
db.session.add(c1)
db.session.commit()
