####FALTA REVISAR LOS TIPOS DE LAS VARIABLES ETC y ver que ocurre si se copian los ficheros scrapeaos


suppressMessages(library(anytime))
suppressMessages(library(ggplot2))
suppressMessages(library(dplyr))
suppressMessages(library(xgboost))
suppressMessages(library(data.table))

whatIsIt<-function(dat){

  dat$isImage<-rep(0,nrow(dat))
  aux<-grep("(.png)|(.jpg)",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isImage<-1
  }
  
  dat$isVideo<-rep(0,nrow(dat))
  aux<-grep("(youtu.be)|(v.redd)|(.mp4)",dat$url,ignore.case = TRUE) 
  if(length(aux)>0){
  dat[aux,]$isVideo<-1
  }
  
  dat$isNews<-rep(0,nrow(dat))
  aux<-grep("news",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isNews<-1
  }
  
  dat$isGif<-rep(0,nrow(dat))
  aux<-grep("gif",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isGif<-1
  }
  
  dat$isOther<-rep(1,nrow(dat))
  dat$isOther<-ifelse((dat$isImage + dat$isVideo + dat$isNews + dat$isSelf + dat$isGif)>0,0,1)
  dat
}

changeClass<-function(dat,vars,classes){
  for(i in 1:length(classes)){
	if(!(vars[i] %in% colnames(dat)))
		next
    if(classes[i]=="numeric"){
      dat[,vars[i]]<-as.numeric(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="integer"){
      dat[,vars[i]]<-as.integer(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="factor"){
      dat[,vars[i]]<-as.factor(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="character"){
      dat[,vars[i]]<-as.character(dat[,vars[i]])
    }
  }
  dat
}

addLvlTrain<-function(dat){
  
  gifLvl<-readLines("files/isGiflevels.txt")
  imgLvl<-readLines("files/isImagelevels.txt")
  newLvl<-readLines("files/isNewslevels.txt")
  othLvl<-readLines("files/isOtherlevels.txt")
  slfLvl<-readLines("files/isSelflevels.txt")
  vidLvl<-readLines("files/isVideolevels.txt")
  subLvl<-readLines("files/subredditlevels.txt")
  tpfLvl<-readLines("files/tipFavlevels.txt")
  wkdLvl<-readLines("files/wdlevels.txt")
  levels(dat$isGif)<-gifLvl
  levels(dat$isImage)<-imgLvl
  levels(dat$isNews)<-newLvl
  levels(dat$isOther)<-othLvl
  levels(dat$isSelf)<-slfLvl
  levels(dat$isVideo)<-vidLvl
  levels(dat$subreddit)<-subLvl
  levels(dat$tipFav)<-tpfLvl
  levels(dat$wd)<-wkdLvl
  dat
}

dumVar<-function(tr){
 
  res<-data.frame(guantanamera=tr[,1])
  cont=2
  for(i in 1:dim(tr)[2]){
    if(is.factor(tr[,i])){
      if(length(levels(tr[,i]))<100){
        lvl<-levels(tr[,i])
        for (j in 1:(length(lvl)-1)){
          res$guant<-ifelse(tr[,i]==lvl[j],1,0)
          res$guant<-as.integer(as.character(res$guant))
          colnames(res)[cont]<-paste(colnames(tr)[i],lvl[j],sep = "")
          cont=cont+1
        }
      }
      else{
        res$guant<-tr[,i]
        colnames(res)[cont]<-colnames(tr)[i]
        cont=cont+1
       
      }
    }
    else{
      res$guant<-tr[,i]
      colnames(res)[cont]<-colnames(tr)[i]
      cont=cont+1
    }
  }
  res<-res[,-1]
  res 
}




findCloser<-function(dat,time){
  ids<-unique(dat$id)
  res<-lapply(ids,function(x){
    aux<-dat[dat$id==x,]
    auxT<-lapply(time,function(y){
    row<-which.min(abs(aux$tsc-y))
    dist<-((aux[row,]$tsc-y))
    auxW<-aux[row,colnames(aux) %in% c("id","score","num_comments")]
	auxW<-auxW[,c(2,3,1)]
    auxW$dist<-dist
    colnames(auxW)<-c("id",paste("score",(y/60),sep="_"),paste("num_comments",(y/60),sep="_"),paste("dist",(y/60),sep="_"))
    auxW
    })
    aux<-bind_cols(auxT)
    aux
  })
  bind_rows(res)
  
}
traza<-c()
##Read the data
setwd("/home/papis/Escritorio/willItBurnBotOld/burnItBot/writer//")
#wd<-getwd()
#setwd("temp")
#temp = list.files(pattern="*.csv")
#myfiles = lapply(temp, read.csv)
#dat<-myfiles[[1]]
#colClasses=c()
#for(i in 2:length(myfiles)){
#  dat<-rbind(dat,myfiles[[i]])
#}
#setwd(wd)

dat<-read.csv("files/dat.csv")

###BORRAME#####
dat<-dat[,!(colnames(dat) %in% "hot")]
###BORRAME#####


##Read the model
modelC<-xgb.load("files/modelC")
modelR<-xgb.load("files/modelR")

traza<-c(traza,"Datos y modelos leidos")
writeLines(traza,"traza.txt")

##Transformations to the data
dat$tsc<-dat$measured-dat$created
dat$hc<-substr(anytime(dat$created),12,13)
dat$wd<-weekdays(as.Date(substr(anytime(dat$created),1,20),'%Y-%m-%d'),abbreviate = TRUE)
traza<-c(traza,"Modificaciones basicas")
traza<-c(traza,"Esto es nuevo")
writeLines(traza,"traza.txt")

##Remove ids younger than 750 secs
actTime<-acTime<-as.numeric(as.POSIXct(Sys.time()))
aux<-as.data.frame(dat %>% group_by(id) %>% summarise(unique(created)))
idsUse<-aux[actTime-aux[,2]>750,]$id
dat<-dat[dat$id %in% idsUse,]
traza<-c(traza,"Jovenes fuera")
writeLines(traza,"traza.txt")

##Remove ids that burnt or that we have already predicted their deaths
hasNotBurnt<-read.csv("files/itHasNotBurnt.csv")
hasBurnt<-read.csv("files/itHasBurnt.csv")
dat<-dat[!(dat$id %in% hasNotBurnt$id),]
dat<-dat[!(dat$id %in% hasBurnt$id),]
traza<-c(traza,"Adios a los ya quemados")
writeLines(traza,"traza.txt")

if(dim(dat)[1]<1)
	stop("No new posts to analyze yet")

##Revisar esto, a lo mejor se quiere anadir el weekday y el hc se ha pasado a integers y que quitar
dat10<-findCloser(dat,c(300,600))
traza<-c(traza,"dat10 creado")
writeLines(traza,"traza.txt")

if(dim(dat10)[1]!=0){
dat10<-dat10[,-5]

datM<-as.data.frame(dat %>% group_by(id) %>% summarise(hc=unique(hc),wd=unique(wd),title=nchar(as.character(unique(title))),body=unique(body)[1],subreddit=unique(subreddit)))
#datM<-as.data.frame(dat %>% group_by(id) %>% summarise(hot=any(hot=="True"),hc=unique(hc),wd=unique(wd),title=nchar(as.character(unique(title))),body=unique(body)[1],is_self=any(is_self=="True"),subreddit=unique(subreddit)))
datF<-merge(dat10,datM,by.x="id",by.y="id")
traza<-c(traza,"datF creado")
writeLines(traza,"traza.txt")


urlsT<-as.data.frame(dat %>% group_by(id) %>% summarise(url=unique(url),isSelf=unique(as.integer(is_self))))
urlsT$isSelf<-ifelse(urlsT$isSelf==2,1,0)
urlsT<-whatIsIt(urlsT)
datF<-merge(datF,urlsT[,-2],by="id")
traza<-c(traza,"datF merfgeado con urls creado")
writeLines(traza,"traza.txt")

histSub<-read.csv("files/histSub.csv")
datF<-merge(datF,histSub,by="subreddit")

traza<-c(traza,"Cansado de conocerte")
writeLines(traza,"traza.txt")

vars<-readLines("files/dataVariables.txt")
classes<-readLines("files/dataClasses.txt")
datF<-changeClass(datF,vars,classes)
datF<-addLvlTrain(datF)
traza<-c(traza,"Justo antes de las predicciones")
writeLines(traza,"traza.txt")

##Se ha de ambiar la forma en la que un argo pasa a la historia (primero clasificar y luego regresion)
ids<-datF$id
write.csv("yougottadeleteme.csv",x=datF[,-2],row.names=FALSE)
new_ts <- model.matrix(~.+0,data = datF[,-2])
traza<-c(traza,"Dimensiones NEW_TS")
traza<-c(traza,dim(new_ts))
writeLines(traza,"traza.txt")
dtest <- xgb.DMatrix(data = new_ts,label = sample(c(TRUE,FALSE),nrow(datF),replace=TRUE))
preds<-predict(modelC,dtest,predictor="gpu_predictor")
res<-as.data.frame(dat %>% group_by(id) %>% summarise(unique(created)))
aux<-data.frame(id=datF$id,pred=preds)
res<-merge(res,aux,by.x="id",by.y="id")
colnames(res)[2]<-"time"
resNB<-res[res$pred<0.5,c(1,2)]
resB<-res[res$pred>=0.5,c(1,2)]
if(dim(resB)[1]>0){
new_ts <- model.matrix(~.+0,data = datF[preds>=0.5,-2])
dtestR<-xgb.DMatrix(data = new_ts,label = rnorm(nrow(datF[preds>=0.5,])))
traza<-c(traza,"Hey papip aqui si que estoy 123 veces digo")
writeLines(traza,"traza.txt")
predsR<-predict(modelR,dtestR,predictor="gpu_predictor")
resB$time<-resB$time+predsR
}
resNB$time<-rep(0,nrow(resNB))
traza<-c(traza,"Hey papip aqui si que estoy 3 veces digo")
writeLines(traza,"traza.txt")
hasNotBurnt<-rbind(hasNotBurnt,resNB)
write.csv("files/itHasNotBurnt.csv",x=hasNotBurnt,row.names=FALSE)
write.csv("files/itWillBurn.csv",x=resB,row.names=FALSE)
} else{
res<-data.frame(id=c("nothing"),time=c(1))
write.csv("files/itWillBurn.csv",x=res[-1,],row.names=FALSE)
}