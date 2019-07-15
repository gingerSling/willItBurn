bindData<-function(){
  library(dplyr)
  library(data.table)
  setwd("..")
  temp = list.files(pattern="reader")
  temp = paste(temp,"/post.csv",sep="")
  myfiles = lapply(temp,function(x){ fread(x,data.table=FALSE)})
  dat<-myfiles[[1]]
  for(i in 2:length(myfiles)){
    dat<-rbind(dat,myfiles[[i]])
  }
  rownames(dat)<-paste0(dat$id,dat$measured)
  setwd("wholeDat/")
  print("Doing dat")
  if(file.exists("wholeDat.csv")){
    
    aux<-fread("wholeDat.csv",data.table=FALSE)
    rownames<-paste0(aux$id,aux$measured)
    aux<-aux[!(duplicated(rownames)),]
    rownames(aux)<-paste0(aux$id,aux$measured)
    dat<-dat[!(rownames(dat) %in% rownames(aux)),]
    dat<-rbind(aux,dat)
    #fwrite(file="wholeDat.csv",x=dat)
    
  }
  else{
    
    fwrite("wholeDat.csv",x=dat,row.names = FALSE)
  }
  hot<-read.csv("../server/whosHot.csv")
  top<-read.csv("../server/whosTop.csv")
  print("Dat done")
  if(file.exists("whosHot.csv")){
    
    aux<-fread("whosHot.csv",data.table=FALSE)
	print(dim(hot))
	print(dim(aux))
    hot<-rbind(aux,hot)
	print(colnames(hot))
	hot<-as.data.frame(hot %>% group_by(id) %>% summarise(min(time)))
	print("was")
    fwrite("whosHot.csv",x=hot,row.names = FALSE)
    
  }
  else{
    
    fwrite("whosHot.csv",x=hot,row.names = FALSE)
  }  
  print("Hot done")
  if(file.exists("whosTop.csv")){
    
    aux<-fread("whosTop.csv",data.table=FALSE)
    top<-rbind(aux,top)
	top<-as.data.frame(top %>% group_by(id) %>% summarise(min(time)))
    fwrite("whosTop.csv",x=top,row.names = FALSE)
    
  }
  else{
    
    fwrite("whosTop.csv",x=top,row.names = FALSE)
  }
}
bindData()