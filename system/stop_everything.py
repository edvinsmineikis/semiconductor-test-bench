import instruments

try:
    cb = instruments.ControlBoard()
    cb.query('disableHiVds 0')
    cb.query('disableHiVg 0')
    cb.query('disableHiVgRelay 0')
    cb.query('disableTempController 0')
    cb.query('disablePwmRelay 0')
    cb.query('disableFan 0')
except:
    pass

try:
    ps = instruments.PowerSupply()
    ps.query('OUTP OFF')
    ps.query('SYST:LOCK OFF')
except:
    pass


