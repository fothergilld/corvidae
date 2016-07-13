import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

#packages
forecast = importr('forecast')


def main(historic_data,start_date, method='additive',damped='TRUE'):

  #create R object
  rob = robjects.r('''
          f <- function(r,start_date, method, verbose=FALSE) {
              start_date <- as.Date(start_date)
              visitsTS<- ts(r, 
                             start= c(as.numeric(format(start_date, "%Y")),as.numeric(format(start_date, "%m"))), 
                             frequency= 12
                             )
              hw(visitsTS, seasonal=method, damped=TRUE,h=24)
          }
          ''')
  
  rob2 = robjects.r('''         
          g <- function(fcast) {
            accuracy(fcast)
          }
          ''')
  
  #create R vector from list
  x = robjects.IntVector(historic_data)
  # extract function from R object
  r_f = robjects.globalenv['f']
  r_g = robjects.globalenv['g']

  #pass historic data to R function
  res = r_f(x,start_date, method)
  acc = r_g(res)
  return res, acc    
  
def write_to_csv():
    write_file = open('/forecast.csv', 'wb')

    commaout = csv.writer(write_file, dialect=csv.excel)
    for row in res:
        commaout.writerow(row)


if __name__ == '__main__':
    main()