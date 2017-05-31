# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Agtagenttypes(models.Model):
    agenttypeid = models.IntegerField(primary_key=True, db_column='agentTypeID') # Field name made lowercase.
    agenttype = models.CharField(max_length=150, db_column='agentType', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'agtAgentTypes'

class Agtagents(models.Model):
    agentid = models.IntegerField(primary_key=True, db_column='agentID') # Field name made lowercase.
    divisionid = models.IntegerField(null=True, db_column='divisionID', blank=True) # Field name made lowercase.
    corporationid = models.IntegerField(null=True, db_column='corporationID', blank=True) # Field name made lowercase.
    locationid = models.IntegerField(null=True, db_column='locationID', blank=True) # Field name made lowercase.
    level = models.IntegerField(null=True, blank=True)
    quality = models.IntegerField(null=True, blank=True)
    agenttypeid = models.IntegerField(null=True, db_column='agentTypeID', blank=True) # Field name made lowercase.
    islocator = models.IntegerField(null=True, db_column='isLocator', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'agtAgents'

class Agtresearchagents(models.Model):
    agentid = models.IntegerField(primary_key=True, db_column='agentID') # Field name made lowercase.
    typeid = models.IntegerField(db_column='typeID') # Field name made lowercase.
    class Meta:
        db_table = 'agtResearchAgents'

class Chrancestries(models.Model):
    ancestryid = models.IntegerField(primary_key=True, db_column='ancestryID') # Field name made lowercase.
    ancestryname = models.CharField(max_length=300, db_column='ancestryName', blank=True) # Field name made lowercase.
    bloodlineid = models.IntegerField(null=True, db_column='bloodlineID', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    perception = models.IntegerField(null=True, blank=True)
    willpower = models.IntegerField(null=True, blank=True)
    charisma = models.IntegerField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)
    intelligence = models.IntegerField(null=True, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    shortdescription = models.CharField(max_length=1500, db_column='shortDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'chrAncestries'

class Chrattributes(models.Model):
    attributeid = models.IntegerField(primary_key=True, db_column='attributeID') # Field name made lowercase.
    attributename = models.CharField(max_length=300, db_column='attributeName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    shortdescription = models.CharField(max_length=1500, db_column='shortDescription', blank=True) # Field name made lowercase.
    notes = models.CharField(max_length=1500, blank=True)
    class Meta:
        db_table = 'chrAttributes'

class Chrbloodlines(models.Model):
    bloodlineid = models.IntegerField(primary_key=True, db_column='bloodlineID') # Field name made lowercase.
    bloodlinename = models.CharField(max_length=300, db_column='bloodlineName', blank=True) # Field name made lowercase.
    raceid = models.IntegerField(null=True, db_column='raceID', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    maledescription = models.CharField(max_length=3000, db_column='maleDescription', blank=True) # Field name made lowercase.
    femaledescription = models.CharField(max_length=3000, db_column='femaleDescription', blank=True) # Field name made lowercase.
    shiptypeid = models.IntegerField(null=True, db_column='shipTypeID', blank=True) # Field name made lowercase.
    corporationid = models.IntegerField(null=True, db_column='corporationID', blank=True) # Field name made lowercase.
    perception = models.IntegerField(null=True, blank=True)
    willpower = models.IntegerField(null=True, blank=True)
    charisma = models.IntegerField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)
    intelligence = models.IntegerField(null=True, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    shortdescription = models.CharField(max_length=1500, db_column='shortDescription', blank=True) # Field name made lowercase.
    shortmaledescription = models.CharField(max_length=1500, db_column='shortMaleDescription', blank=True) # Field name made lowercase.
    shortfemaledescription = models.CharField(max_length=1500, db_column='shortFemaleDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'chrBloodlines'

class Chrfactions(models.Model):
    factionid = models.IntegerField(primary_key=True, db_column='factionID') # Field name made lowercase.
    factionname = models.CharField(max_length=300, db_column='factionName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    raceids = models.IntegerField(null=True, db_column='raceIDs', blank=True) # Field name made lowercase.
    solarsystemid = models.IntegerField(null=True, db_column='solarSystemID', blank=True) # Field name made lowercase.
    corporationid = models.IntegerField(null=True, db_column='corporationID', blank=True) # Field name made lowercase.
    sizefactor = models.FloatField(null=True, db_column='sizeFactor', blank=True) # Field name made lowercase.
    stationcount = models.IntegerField(null=True, db_column='stationCount', blank=True) # Field name made lowercase.
    stationsystemcount = models.IntegerField(null=True, db_column='stationSystemCount', blank=True) # Field name made lowercase.
    militiacorporationid = models.IntegerField(null=True, db_column='militiaCorporationID', blank=True) # Field name made lowercase.
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'chrFactions'

class Chrraces(models.Model):
    raceid = models.IntegerField(primary_key=True, db_column='raceID') # Field name made lowercase.
    racename = models.CharField(max_length=300, db_column='raceName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    shortdescription = models.CharField(max_length=1500, db_column='shortDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'chrRaces'

class Crpactivities(models.Model):
    activityid = models.IntegerField(primary_key=True, db_column='activityID') # Field name made lowercase.
    activityname = models.CharField(max_length=300, db_column='activityName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    class Meta:
        db_table = 'crpActivities'

class Crpnpccorporationdivisions(models.Model):
    corporationid = models.IntegerField(primary_key=True, db_column='corporationID') # Field name made lowercase.
    divisionid = models.IntegerField(primary_key=True, db_column='divisionID') # Field name made lowercase.
    size = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'crpNPCCorporationDivisions'

class Crpnpccorporationresearchfields(models.Model):
    skillid = models.IntegerField(primary_key=True, db_column='skillID') # Field name made lowercase.
    corporationid = models.IntegerField(primary_key=True, db_column='corporationID') # Field name made lowercase.
    class Meta:
        db_table = 'crpNPCCorporationResearchFields'

class Crpnpccorporationtrades(models.Model):
    corporationid = models.IntegerField(primary_key=True, db_column='corporationID') # Field name made lowercase.
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    class Meta:
        db_table = 'crpNPCCorporationTrades'

class Crpnpccorporations(models.Model):
    corporationid = models.IntegerField(primary_key=True, db_column='corporationID') # Field name made lowercase.
    size = models.CharField(max_length=3, blank=True)
    extent = models.CharField(max_length=3, blank=True)
    solarsystemid = models.IntegerField(null=True, db_column='solarSystemID', blank=True) # Field name made lowercase.
    investorid1 = models.IntegerField(null=True, db_column='investorID1', blank=True) # Field name made lowercase.
    investorshares1 = models.IntegerField(null=True, db_column='investorShares1', blank=True) # Field name made lowercase.
    investorid2 = models.IntegerField(null=True, db_column='investorID2', blank=True) # Field name made lowercase.
    investorshares2 = models.IntegerField(null=True, db_column='investorShares2', blank=True) # Field name made lowercase.
    investorid3 = models.IntegerField(null=True, db_column='investorID3', blank=True) # Field name made lowercase.
    investorshares3 = models.IntegerField(null=True, db_column='investorShares3', blank=True) # Field name made lowercase.
    investorid4 = models.IntegerField(null=True, db_column='investorID4', blank=True) # Field name made lowercase.
    investorshares4 = models.IntegerField(null=True, db_column='investorShares4', blank=True) # Field name made lowercase.
    friendid = models.IntegerField(null=True, db_column='friendID', blank=True) # Field name made lowercase.
    enemyid = models.IntegerField(null=True, db_column='enemyID', blank=True) # Field name made lowercase.
    publicshares = models.BigIntegerField(null=True, db_column='publicShares', blank=True) # Field name made lowercase.
    initialprice = models.IntegerField(null=True, db_column='initialPrice', blank=True) # Field name made lowercase.
    minsecurity = models.FloatField(null=True, db_column='minSecurity', blank=True) # Field name made lowercase.
    scattered = models.IntegerField(null=True, blank=True)
    fringe = models.IntegerField(null=True, blank=True)
    corridor = models.IntegerField(null=True, blank=True)
    hub = models.IntegerField(null=True, blank=True)
    border = models.IntegerField(null=True, blank=True)
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    sizefactor = models.FloatField(null=True, db_column='sizeFactor', blank=True) # Field name made lowercase.
    stationcount = models.IntegerField(null=True, db_column='stationCount', blank=True) # Field name made lowercase.
    stationsystemcount = models.IntegerField(null=True, db_column='stationSystemCount', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=12000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'crpNPCCorporations'

class Crpnpcdivisions(models.Model):
    divisionid = models.IntegerField(primary_key=True, db_column='divisionID') # Field name made lowercase.
    divisionname = models.CharField(max_length=300, db_column='divisionName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    leadertype = models.CharField(max_length=300, db_column='leaderType', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'crpNPCDivisions'

class Crtcategories(models.Model):
    categoryid = models.IntegerField(primary_key=True, db_column='categoryID') # Field name made lowercase.
    description = models.CharField(max_length=1500, blank=True)
    categoryname = models.CharField(max_length=768, db_column='categoryName', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'crtCategories'

class Crtcertificates(models.Model):
    certificateid = models.IntegerField(primary_key=True, db_column='certificateID') # Field name made lowercase.
    categoryid = models.IntegerField(null=True, db_column='categoryID', blank=True) # Field name made lowercase.
    classid = models.IntegerField(null=True, db_column='classID', blank=True) # Field name made lowercase.
    grade = models.IntegerField(null=True, blank=True)
    corpid = models.IntegerField(null=True, db_column='corpID', blank=True) # Field name made lowercase.
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=1500, blank=True)
    class Meta:
        db_table = 'crtCertificates'

class Crtclasses(models.Model):
    classid = models.IntegerField(primary_key=True, db_column='classID') # Field name made lowercase.
    description = models.CharField(max_length=1500, blank=True)
    classname = models.CharField(max_length=768, db_column='className', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'crtClasses'

class Crtrecommendations(models.Model):
    recommendationid = models.IntegerField(primary_key=True, db_column='recommendationID') # Field name made lowercase.
    shiptypeid = models.IntegerField(null=True, db_column='shipTypeID', blank=True) # Field name made lowercase.
    certificateid = models.IntegerField(null=True, db_column='certificateID', blank=True) # Field name made lowercase.
    recommendationlevel = models.IntegerField(db_column='recommendationLevel') # Field name made lowercase.
    class Meta:
        db_table = 'crtRecommendations'

class Crtrelationships(models.Model):
    relationshipid = models.IntegerField(primary_key=True, db_column='relationshipID') # Field name made lowercase.
    parentid = models.IntegerField(null=True, db_column='parentID', blank=True) # Field name made lowercase.
    parenttypeid = models.IntegerField(null=True, db_column='parentTypeID', blank=True) # Field name made lowercase.
    parentlevel = models.IntegerField(null=True, db_column='parentLevel', blank=True) # Field name made lowercase.
    childid = models.IntegerField(null=True, db_column='childID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'crtRelationships'

class Dgmattributecategories(models.Model):
    categoryid = models.IntegerField(primary_key=True, db_column='categoryID') # Field name made lowercase.
    categoryname = models.CharField(max_length=150, db_column='categoryName', blank=True) # Field name made lowercase.
    categorydescription = models.CharField(max_length=600, db_column='categoryDescription', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'dgmAttributeCategories'

class Dgmattributetypes(models.Model):
    attributeid = models.IntegerField(primary_key=True, db_column='attributeID') # Field name made lowercase.
    attributename = models.CharField(max_length=300, db_column='attributeName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    defaultvalue = models.FloatField(null=True, db_column='defaultValue', blank=True) # Field name made lowercase.
    published = models.IntegerField(null=True, blank=True)
    displayname = models.CharField(max_length=300, db_column='displayName', blank=True) # Field name made lowercase.
    unitid = models.IntegerField(null=True, db_column='unitID', blank=True) # Field name made lowercase.
    stackable = models.IntegerField(null=True, blank=True)
    highisgood = models.IntegerField(null=True, db_column='highIsGood', blank=True) # Field name made lowercase.
    categoryid = models.IntegerField(null=True, db_column='categoryID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'dgmAttributeTypes'

class Dgmeffects(models.Model):
    effectid = models.IntegerField(primary_key=True, db_column='effectID') # Field name made lowercase.
    effectname = models.CharField(max_length=1200, db_column='effectName', blank=True) # Field name made lowercase.
    effectcategory = models.IntegerField(null=True, db_column='effectCategory', blank=True) # Field name made lowercase.
    preexpression = models.IntegerField(null=True, db_column='preExpression', blank=True) # Field name made lowercase.
    postexpression = models.IntegerField(null=True, db_column='postExpression', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    guid = models.CharField(max_length=180, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    isoffensive = models.IntegerField(null=True, db_column='isOffensive', blank=True) # Field name made lowercase.
    isassistance = models.IntegerField(null=True, db_column='isAssistance', blank=True) # Field name made lowercase.
    durationattributeid = models.IntegerField(null=True, db_column='durationAttributeID', blank=True) # Field name made lowercase.
    trackingspeedattributeid = models.IntegerField(null=True, db_column='trackingSpeedAttributeID', blank=True) # Field name made lowercase.
    dischargeattributeid = models.IntegerField(null=True, db_column='dischargeAttributeID', blank=True) # Field name made lowercase.
    rangeattributeid = models.IntegerField(null=True, db_column='rangeAttributeID', blank=True) # Field name made lowercase.
    falloffattributeid = models.IntegerField(null=True, db_column='falloffAttributeID', blank=True) # Field name made lowercase.
    disallowautorepeat = models.IntegerField(null=True, db_column='disallowAutoRepeat', blank=True) # Field name made lowercase.
    published = models.IntegerField(null=True, blank=True)
    displayname = models.CharField(max_length=300, db_column='displayName', blank=True) # Field name made lowercase.
    iswarpsafe = models.IntegerField(null=True, db_column='isWarpSafe', blank=True) # Field name made lowercase.
    rangechance = models.IntegerField(null=True, db_column='rangeChance', blank=True) # Field name made lowercase.
    electronicchance = models.IntegerField(null=True, db_column='electronicChance', blank=True) # Field name made lowercase.
    propulsionchance = models.IntegerField(null=True, db_column='propulsionChance', blank=True) # Field name made lowercase.
    distribution = models.IntegerField(null=True, blank=True)
    sfxname = models.CharField(max_length=60, db_column='sfxName', blank=True) # Field name made lowercase.
    npcusagechanceattributeid = models.IntegerField(null=True, db_column='npcUsageChanceAttributeID', blank=True) # Field name made lowercase.
    npcactivationchanceattributeid = models.IntegerField(null=True, db_column='npcActivationChanceAttributeID', blank=True) # Field name made lowercase.
    fittingusagechanceattributeid = models.IntegerField(null=True, db_column='fittingUsageChanceAttributeID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'dgmEffects'

class Dgmtypeattributes(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    attributeid = models.IntegerField(primary_key=True, db_column='attributeID') # Field name made lowercase.
    valueint = models.IntegerField(null=True, db_column='valueInt', blank=True) # Field name made lowercase.
    valuefloat = models.FloatField(null=True, db_column='valueFloat', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'dgmTypeAttributes'

class Dgmtypeeffects(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    effectid = models.IntegerField(primary_key=True, db_column='effectID') # Field name made lowercase.
    isdefault = models.IntegerField(null=True, db_column='isDefault', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'dgmTypeEffects'

class Evegraphics(models.Model):
    graphicid = models.IntegerField(primary_key=True, db_column='graphicID') # Field name made lowercase.
    graphicfile = models.CharField(max_length=1500, db_column='graphicFile') # Field name made lowercase.
    description = models.TextField(blank=True)
    obsolete = models.IntegerField(null=True, blank=True)
    graphictype = models.CharField(max_length=300, db_column='graphicType', blank=True) # Field name made lowercase.
    collidable = models.IntegerField(null=True, blank=True)
    explosionid = models.IntegerField(null=True, db_column='explosionID', blank=True) # Field name made lowercase.
    directoryid = models.IntegerField(null=True, db_column='directoryID', blank=True) # Field name made lowercase.
    graphicname = models.TextField(db_column='graphicName', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'eveGraphics'

class Eveicons(models.Model):
    iconid = models.IntegerField(primary_key=True, db_column='iconID') # Field name made lowercase.
    iconfile = models.CharField(max_length=1500, db_column='iconFile') # Field name made lowercase.
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'eveIcons'

class Eveunits(models.Model):
    unitid = models.IntegerField(primary_key=True, db_column='unitID') # Field name made lowercase.
    unitname = models.CharField(max_length=300, db_column='unitName', blank=True) # Field name made lowercase.
    displayname = models.CharField(max_length=150, db_column='displayName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    class Meta:
        db_table = 'eveUnits'

class Invblueprinttypes(models.Model):
    blueprinttypeid = models.IntegerField(primary_key=True, db_column='blueprintTypeID') # Field name made lowercase.
    parentblueprinttypeid = models.IntegerField(null=True, db_column='parentBlueprintTypeID', blank=True) # Field name made lowercase.
    producttypeid = models.IntegerField(null=True, db_column='productTypeID', blank=True) # Field name made lowercase.
    productiontime = models.IntegerField(null=True, db_column='productionTime', blank=True) # Field name made lowercase.
    techlevel = models.IntegerField(null=True, db_column='techLevel', blank=True) # Field name made lowercase.
    researchproductivitytime = models.IntegerField(null=True, db_column='researchProductivityTime', blank=True) # Field name made lowercase.
    researchmaterialtime = models.IntegerField(null=True, db_column='researchMaterialTime', blank=True) # Field name made lowercase.
    researchcopytime = models.IntegerField(null=True, db_column='researchCopyTime', blank=True) # Field name made lowercase.
    researchtechtime = models.IntegerField(null=True, db_column='researchTechTime', blank=True) # Field name made lowercase.
    productivitymodifier = models.IntegerField(null=True, db_column='productivityModifier', blank=True) # Field name made lowercase.
    materialmodifier = models.IntegerField(null=True, db_column='materialModifier', blank=True) # Field name made lowercase.
    wastefactor = models.IntegerField(null=True, db_column='wasteFactor', blank=True) # Field name made lowercase.
    maxproductionlimit = models.IntegerField(null=True, db_column='maxProductionLimit', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invBlueprintTypes'

class Invcategories(models.Model):
    categoryid = models.IntegerField(primary_key=True, db_column='categoryID') # Field name made lowercase.
    categoryname = models.CharField(max_length=300, db_column='categoryName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=9000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    published = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'invCategories'

class Invcontrabandtypes(models.Model):
    factionid = models.IntegerField(primary_key=True, db_column='factionID') # Field name made lowercase.
    typeid = models.IntegerField(db_column='typeID') # Field name made lowercase.
    standingloss = models.FloatField(null=True, db_column='standingLoss', blank=True) # Field name made lowercase.
    confiscateminsec = models.FloatField(null=True, db_column='confiscateMinSec', blank=True) # Field name made lowercase.
    finebyvalue = models.FloatField(null=True, db_column='fineByValue', blank=True) # Field name made lowercase.
    attackminsec = models.FloatField(null=True, db_column='attackMinSec', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invContrabandTypes'

class Invcontroltowerresourcepurposes(models.Model):
    purpose = models.IntegerField(primary_key=True)
    purposetext = models.CharField(max_length=300, db_column='purposeText', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invControlTowerResourcePurposes'

class Invcontroltowerresources(models.Model):
    controltowertypeid = models.IntegerField(primary_key=True, db_column='controlTowerTypeID') # Field name made lowercase.
    resourcetypeid = models.IntegerField(primary_key=True, db_column='resourceTypeID') # Field name made lowercase.
    purpose = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    minsecuritylevel = models.FloatField(null=True, db_column='minSecurityLevel', blank=True) # Field name made lowercase.
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invControlTowerResources'

class Invflags(models.Model):
    flagid = models.IntegerField(primary_key=True, db_column='flagID') # Field name made lowercase.
    flagname = models.CharField(max_length=600, db_column='flagName', blank=True) # Field name made lowercase.
    flagtext = models.CharField(max_length=300, db_column='flagText', blank=True) # Field name made lowercase.
    orderid = models.IntegerField(null=True, db_column='orderID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invFlags'

class Invgroups(models.Model):
    groupid = models.IntegerField(primary_key=True, db_column='groupID') # Field name made lowercase.
    categoryid = models.IntegerField(null=True, db_column='categoryID', blank=True) # Field name made lowercase.
    groupname = models.CharField(max_length=300, db_column='groupName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=9000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    usebaseprice = models.IntegerField(null=True, db_column='useBasePrice', blank=True) # Field name made lowercase.
    allowmanufacture = models.IntegerField(null=True, db_column='allowManufacture', blank=True) # Field name made lowercase.
    allowrecycler = models.IntegerField(null=True, db_column='allowRecycler', blank=True) # Field name made lowercase.
    anchored = models.IntegerField(null=True, blank=True)
    anchorable = models.IntegerField(null=True, blank=True)
    fittablenonsingleton = models.IntegerField(null=True, db_column='fittableNonSingleton', blank=True) # Field name made lowercase.
    published = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'invGroups'

class Invitems(models.Model):
    itemid = models.BigIntegerField(primary_key=True, db_column='itemID') # Field name made lowercase.
    typeid = models.IntegerField(db_column='typeID') # Field name made lowercase.
    ownerid = models.IntegerField(db_column='ownerID') # Field name made lowercase.
    locationid = models.BigIntegerField(db_column='locationID') # Field name made lowercase.
    flagid = models.IntegerField(db_column='flagID') # Field name made lowercase.
    quantity = models.IntegerField()
    class Meta:
        db_table = 'invItems'

class Invmarketgroups(models.Model):
    marketgroupid = models.IntegerField(primary_key=True, db_column='marketGroupID') # Field name made lowercase.
    parentgroupid = models.IntegerField(null=True, db_column='parentGroupID', blank=True) # Field name made lowercase.
    marketgroupname = models.CharField(max_length=300, db_column='marketGroupName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=9000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    hastypes = models.IntegerField(null=True, db_column='hasTypes', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invMarketGroups'

class Invmetagroups(models.Model):
    metagroupid = models.IntegerField(primary_key=True, db_column='metaGroupID') # Field name made lowercase.
    metagroupname = models.CharField(max_length=300, db_column='metaGroupName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invMetaGroups'

class Invmetatypes(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    parenttypeid = models.IntegerField(null=True, db_column='parentTypeID', blank=True) # Field name made lowercase.
    metagroupid = models.IntegerField(null=True, db_column='metaGroupID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invMetaTypes'

class Invnames(models.Model):
    itemid = models.BigIntegerField(primary_key=True, db_column='itemID') # Field name made lowercase.
    itemname = models.CharField(max_length=600, db_column='itemName') # Field name made lowercase.
    class Meta:
        db_table = 'invNames'

class Invpositions(models.Model):
    itemid = models.BigIntegerField(primary_key=True, db_column='itemID') # Field name made lowercase.
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    yaw = models.FloatField(null=True, blank=True)
    pitch = models.FloatField(null=True, blank=True)
    roll = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'invPositions'

class Invtypematerials(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    materialtypeid = models.IntegerField(primary_key=True, db_column='materialTypeID') # Field name made lowercase.
    quantity = models.IntegerField()
    class Meta:
        db_table = 'invTypeMaterials'

class Invtypereactions(models.Model):
    reactiontypeid = models.IntegerField(primary_key=True, db_column='reactionTypeID') # Field name made lowercase.
    input = models.IntegerField(primary_key=True)
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    quantity = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'invTypeReactions'

class Invtypes(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    groupid = models.IntegerField(null=True, db_column='groupID', blank=True) # Field name made lowercase.
    typename = models.CharField(max_length=300, db_column='typeName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=9000, blank=True)
    radius = models.FloatField(null=True, blank=True)
    mass = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    capacity = models.FloatField(null=True, blank=True)
    portionsize = models.IntegerField(null=True, db_column='portionSize', blank=True) # Field name made lowercase.
    raceid = models.IntegerField(null=True, db_column='raceID', blank=True) # Field name made lowercase.
    baseprice = models.DecimalField(decimal_places=4, null=True, max_digits=21, db_column='basePrice', blank=True) # Field name made lowercase.
    published = models.IntegerField(null=True, blank=True)
    marketgroupid = models.IntegerField(null=True, db_column='marketGroupID', blank=True) # Field name made lowercase.
    chanceofduplicating = models.FloatField(null=True, db_column='chanceOfDuplicating', blank=True) # Field name made lowercase.
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invTypes'

class Invuniquenames(models.Model):
    itemid = models.IntegerField(primary_key=True, db_column='itemID') # Field name made lowercase.
    itemname = models.CharField(max_length=600, db_column='itemName') # Field name made lowercase.
    groupid = models.IntegerField(null=True, db_column='groupID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'invUniqueNames'

class Mapcelestialstatistics(models.Model):
    celestialid = models.IntegerField(primary_key=True, db_column='celestialID') # Field name made lowercase.
    temperature = models.FloatField(null=True, blank=True)
    spectralclass = models.CharField(max_length=30, db_column='spectralClass', blank=True) # Field name made lowercase.
    luminosity = models.FloatField(null=True, blank=True)
    age = models.FloatField(null=True, blank=True)
    life = models.FloatField(null=True, blank=True)
    orbitradius = models.FloatField(null=True, db_column='orbitRadius', blank=True) # Field name made lowercase.
    eccentricity = models.FloatField(null=True, blank=True)
    massdust = models.FloatField(null=True, db_column='massDust', blank=True) # Field name made lowercase.
    massgas = models.FloatField(null=True, db_column='massGas', blank=True) # Field name made lowercase.
    fragmented = models.IntegerField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    surfacegravity = models.FloatField(null=True, db_column='surfaceGravity', blank=True) # Field name made lowercase.
    escapevelocity = models.FloatField(null=True, db_column='escapeVelocity', blank=True) # Field name made lowercase.
    orbitperiod = models.FloatField(null=True, db_column='orbitPeriod', blank=True) # Field name made lowercase.
    rotationrate = models.FloatField(null=True, db_column='rotationRate', blank=True) # Field name made lowercase.
    locked = models.IntegerField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    mass = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'mapCelestialStatistics'

class Mapconstellationjumps(models.Model):
    fromregionid = models.IntegerField(null=True, db_column='fromRegionID', blank=True) # Field name made lowercase.
    fromconstellationid = models.IntegerField(primary_key=True, db_column='fromConstellationID') # Field name made lowercase.
    toconstellationid = models.IntegerField(primary_key=True, db_column='toConstellationID') # Field name made lowercase.
    toregionid = models.IntegerField(null=True, db_column='toRegionID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapConstellationJumps'

class Mapconstellations(models.Model):
    regionid = models.IntegerField(null=True, db_column='regionID', blank=True) # Field name made lowercase.
    constellationid = models.IntegerField(primary_key=True, db_column='constellationID') # Field name made lowercase.
    constellationname = models.CharField(max_length=300, db_column='constellationName', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xmin = models.FloatField(null=True, db_column='xMin', blank=True) # Field name made lowercase.
    xmax = models.FloatField(null=True, db_column='xMax', blank=True) # Field name made lowercase.
    ymin = models.FloatField(null=True, db_column='yMin', blank=True) # Field name made lowercase.
    ymax = models.FloatField(null=True, db_column='yMax', blank=True) # Field name made lowercase.
    zmin = models.FloatField(null=True, db_column='zMin', blank=True) # Field name made lowercase.
    zmax = models.FloatField(null=True, db_column='zMax', blank=True) # Field name made lowercase.
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'mapConstellations'

class Mapdenormalize(models.Model):
    itemid = models.IntegerField(primary_key=True, db_column='itemID') # Field name made lowercase.
    typeid = models.IntegerField(null=True, db_column='typeID', blank=True) # Field name made lowercase.
    groupid = models.IntegerField(null=True, db_column='groupID', blank=True) # Field name made lowercase.
    solarsystemid = models.IntegerField(null=True, db_column='solarSystemID', blank=True) # Field name made lowercase.
    constellationid = models.IntegerField(null=True, db_column='constellationID', blank=True) # Field name made lowercase.
    regionid = models.IntegerField(null=True, db_column='regionID', blank=True) # Field name made lowercase.
    orbitid = models.IntegerField(null=True, db_column='orbitID', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    itemname = models.CharField(max_length=300, db_column='itemName', blank=True) # Field name made lowercase.
    security = models.FloatField(null=True, blank=True)
    celestialindex = models.IntegerField(null=True, db_column='celestialIndex', blank=True) # Field name made lowercase.
    orbitindex = models.IntegerField(null=True, db_column='orbitIndex', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapDenormalize'

class Mapjumps(models.Model):
    stargateid = models.IntegerField(primary_key=True, db_column='stargateID') # Field name made lowercase.
    celestialid = models.IntegerField(null=True, db_column='celestialID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapJumps'

class Maplandmarks(models.Model):
    landmarkid = models.IntegerField(primary_key=True, db_column='landmarkID') # Field name made lowercase.
    landmarkname = models.CharField(max_length=300, db_column='landmarkName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=21000, blank=True)
    locationid = models.IntegerField(null=True, db_column='locationID', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    iconid = models.IntegerField(null=True, db_column='iconID', blank=True) # Field name made lowercase.
    importance = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'mapLandmarks'

class Maplocationscenes(models.Model):
    locationid = models.IntegerField(primary_key=True, db_column='locationID') # Field name made lowercase.
    graphicid = models.IntegerField(null=True, db_column='graphicID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapLocationScenes'

class Maplocationwormholeclasses(models.Model):
    locationid = models.IntegerField(primary_key=True, db_column='locationID') # Field name made lowercase.
    wormholeclassid = models.IntegerField(null=True, db_column='wormholeClassID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapLocationWormholeClasses'

class Mapregionjumps(models.Model):
    fromregionid = models.IntegerField(primary_key=True, db_column='fromRegionID') # Field name made lowercase.
    toregionid = models.IntegerField(primary_key=True, db_column='toRegionID') # Field name made lowercase.
    class Meta:
        db_table = 'mapRegionJumps'

class Mapregions(models.Model):
    regionid = models.IntegerField(primary_key=True, db_column='regionID') # Field name made lowercase.
    regionname = models.CharField(max_length=300, db_column='regionName', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xmin = models.FloatField(null=True, db_column='xMin', blank=True) # Field name made lowercase.
    xmax = models.FloatField(null=True, db_column='xMax', blank=True) # Field name made lowercase.
    ymin = models.FloatField(null=True, db_column='yMin', blank=True) # Field name made lowercase.
    ymax = models.FloatField(null=True, db_column='yMax', blank=True) # Field name made lowercase.
    zmin = models.FloatField(null=True, db_column='zMin', blank=True) # Field name made lowercase.
    zmax = models.FloatField(null=True, db_column='zMax', blank=True) # Field name made lowercase.
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'mapRegions'

class Mapsolarsystemjumps(models.Model):
    fromregionid = models.IntegerField(null=True, db_column='fromRegionID', blank=True) # Field name made lowercase.
    fromconstellationid = models.IntegerField(null=True, db_column='fromConstellationID', blank=True) # Field name made lowercase.
    fromsolarsystemid = models.IntegerField(primary_key=True, db_column='fromSolarSystemID') # Field name made lowercase.
    tosolarsystemid = models.IntegerField(primary_key=True, db_column='toSolarSystemID') # Field name made lowercase.
    toconstellationid = models.IntegerField(null=True, db_column='toConstellationID', blank=True) # Field name made lowercase.
    toregionid = models.IntegerField(null=True, db_column='toRegionID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapSolarSystemJumps'

class Mapsolarsystems(models.Model):
    regionid = models.IntegerField(null=True, db_column='regionID', blank=True) # Field name made lowercase.
    constellationid = models.IntegerField(null=True, db_column='constellationID', blank=True) # Field name made lowercase.
    solarsystemid = models.IntegerField(primary_key=True, db_column='solarSystemID') # Field name made lowercase.
    solarsystemname = models.CharField(max_length=300, db_column='solarSystemName', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xmin = models.FloatField(null=True, db_column='xMin', blank=True) # Field name made lowercase.
    xmax = models.FloatField(null=True, db_column='xMax', blank=True) # Field name made lowercase.
    ymin = models.FloatField(null=True, db_column='yMin', blank=True) # Field name made lowercase.
    ymax = models.FloatField(null=True, db_column='yMax', blank=True) # Field name made lowercase.
    zmin = models.FloatField(null=True, db_column='zMin', blank=True) # Field name made lowercase.
    zmax = models.FloatField(null=True, db_column='zMax', blank=True) # Field name made lowercase.
    luminosity = models.FloatField(null=True, blank=True)
    border = models.IntegerField(null=True, blank=True)
    fringe = models.IntegerField(null=True, blank=True)
    corridor = models.IntegerField(null=True, blank=True)
    hub = models.IntegerField(null=True, blank=True)
    international = models.IntegerField(null=True, blank=True)
    regional = models.IntegerField(null=True, blank=True)
    constellation = models.IntegerField(null=True, blank=True)
    security = models.FloatField(null=True, blank=True)
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    radius = models.FloatField(null=True, blank=True)
    suntypeid = models.IntegerField(null=True, db_column='sunTypeID', blank=True) # Field name made lowercase.
    securityclass = models.CharField(max_length=6, db_column='securityClass', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'mapSolarSystems'

class Mapuniverse(models.Model):
    universeid = models.IntegerField(primary_key=True, db_column='universeID') # Field name made lowercase.
    universename = models.CharField(max_length=300, db_column='universeName', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xmin = models.FloatField(null=True, db_column='xMin', blank=True) # Field name made lowercase.
    xmax = models.FloatField(null=True, db_column='xMax', blank=True) # Field name made lowercase.
    ymin = models.FloatField(null=True, db_column='yMin', blank=True) # Field name made lowercase.
    ymax = models.FloatField(null=True, db_column='yMax', blank=True) # Field name made lowercase.
    zmin = models.FloatField(null=True, db_column='zMin', blank=True) # Field name made lowercase.
    zmax = models.FloatField(null=True, db_column='zMax', blank=True) # Field name made lowercase.
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'mapUniverse'

class Planetschematics(models.Model):
    schematicid = models.IntegerField(primary_key=True, db_column='schematicID') # Field name made lowercase.
    schematicname = models.CharField(max_length=765, db_column='schematicName', blank=True) # Field name made lowercase.
    cycletime = models.IntegerField(null=True, db_column='cycleTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'planetSchematics'

class Planetschematicspinmap(models.Model):
    schematicid = models.IntegerField(primary_key=True, db_column='schematicID') # Field name made lowercase.
    pintypeid = models.IntegerField(primary_key=True, db_column='pinTypeID') # Field name made lowercase.
    class Meta:
        db_table = 'planetSchematicsPinMap'

class Planetschematicstypemap(models.Model):
    schematicid = models.IntegerField(primary_key=True, db_column='schematicID') # Field name made lowercase.
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    quantity = models.IntegerField(null=True, blank=True)
    isinput = models.IntegerField(null=True, db_column='isInput', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'planetSchematicsTypeMap'

class Ramactivities(models.Model):
    activityid = models.IntegerField(primary_key=True, db_column='activityID') # Field name made lowercase.
    activityname = models.CharField(max_length=300, db_column='activityName', blank=True) # Field name made lowercase.
    iconno = models.CharField(max_length=15, db_column='iconNo', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    published = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ramActivities'

class Ramassemblylinestations(models.Model):
    stationid = models.IntegerField(primary_key=True, db_column='stationID') # Field name made lowercase.
    assemblylinetypeid = models.IntegerField(primary_key=True, db_column='assemblyLineTypeID') # Field name made lowercase.
    quantity = models.IntegerField(null=True, blank=True)
    stationtypeid = models.IntegerField(null=True, db_column='stationTypeID', blank=True) # Field name made lowercase.
    ownerid = models.IntegerField(null=True, db_column='ownerID', blank=True) # Field name made lowercase.
    solarsystemid = models.IntegerField(null=True, db_column='solarSystemID', blank=True) # Field name made lowercase.
    regionid = models.IntegerField(null=True, db_column='regionID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'ramAssemblyLineStations'

class Ramassemblylinetypedetailpercategory(models.Model):
    assemblylinetypeid = models.IntegerField(primary_key=True, db_column='assemblyLineTypeID') # Field name made lowercase.
    categoryid = models.IntegerField(primary_key=True, db_column='categoryID') # Field name made lowercase.
    timemultiplier = models.FloatField(null=True, db_column='timeMultiplier', blank=True) # Field name made lowercase.
    materialmultiplier = models.FloatField(null=True, db_column='materialMultiplier', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'ramAssemblyLineTypeDetailPerCategory'

class Ramassemblylinetypedetailpergroup(models.Model):
    assemblylinetypeid = models.IntegerField(primary_key=True, db_column='assemblyLineTypeID') # Field name made lowercase.
    groupid = models.IntegerField(primary_key=True, db_column='groupID') # Field name made lowercase.
    timemultiplier = models.FloatField(null=True, db_column='timeMultiplier', blank=True) # Field name made lowercase.
    materialmultiplier = models.FloatField(null=True, db_column='materialMultiplier', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'ramAssemblyLineTypeDetailPerGroup'

class Ramassemblylinetypes(models.Model):
    assemblylinetypeid = models.IntegerField(primary_key=True, db_column='assemblyLineTypeID') # Field name made lowercase.
    assemblylinetypename = models.CharField(max_length=300, db_column='assemblyLineTypeName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    basetimemultiplier = models.FloatField(null=True, db_column='baseTimeMultiplier', blank=True) # Field name made lowercase.
    basematerialmultiplier = models.FloatField(null=True, db_column='baseMaterialMultiplier', blank=True) # Field name made lowercase.
    volume = models.FloatField(null=True, blank=True)
    activityid = models.IntegerField(null=True, db_column='activityID', blank=True) # Field name made lowercase.
    mincostperhour = models.FloatField(null=True, db_column='minCostPerHour', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'ramAssemblyLineTypes'

class Ramassemblylines(models.Model):
    assemblylineid = models.IntegerField(primary_key=True, db_column='assemblyLineID') # Field name made lowercase.
    assemblylinetypeid = models.IntegerField(null=True, db_column='assemblyLineTypeID', blank=True) # Field name made lowercase.
    containerid = models.IntegerField(null=True, db_column='containerID', blank=True) # Field name made lowercase.
    nextfreetime = models.DateTimeField(null=True, db_column='nextFreeTime', blank=True) # Field name made lowercase.
    uigroupingid = models.IntegerField(null=True, db_column='UIGroupingID', blank=True) # Field name made lowercase.
    costinstall = models.FloatField(null=True, db_column='costInstall', blank=True) # Field name made lowercase.
    costperhour = models.FloatField(null=True, db_column='costPerHour', blank=True) # Field name made lowercase.
    restrictionmask = models.IntegerField(null=True, db_column='restrictionMask', blank=True) # Field name made lowercase.
    discountpergoodstandingpoint = models.FloatField(null=True, db_column='discountPerGoodStandingPoint', blank=True) # Field name made lowercase.
    surchargeperbadstandingpoint = models.FloatField(null=True, db_column='surchargePerBadStandingPoint', blank=True) # Field name made lowercase.
    minimumstanding = models.FloatField(null=True, db_column='minimumStanding', blank=True) # Field name made lowercase.
    minimumcharsecurity = models.FloatField(null=True, db_column='minimumCharSecurity', blank=True) # Field name made lowercase.
    minimumcorpsecurity = models.FloatField(null=True, db_column='minimumCorpSecurity', blank=True) # Field name made lowercase.
    maximumcharsecurity = models.FloatField(null=True, db_column='maximumCharSecurity', blank=True) # Field name made lowercase.
    maximumcorpsecurity = models.FloatField(null=True, db_column='maximumCorpSecurity', blank=True) # Field name made lowercase.
    ownerid = models.IntegerField(null=True, db_column='ownerID', blank=True) # Field name made lowercase.
    activityid = models.IntegerField(null=True, db_column='activityID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'ramAssemblyLines'

class Raminstallationtypecontents(models.Model):
    installationtypeid = models.IntegerField(primary_key=True, db_column='installationTypeID') # Field name made lowercase.
    assemblylinetypeid = models.IntegerField(primary_key=True, db_column='assemblyLineTypeID') # Field name made lowercase.
    quantity = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ramInstallationTypeContents'

class Ramtyperequirements(models.Model):
    typeid = models.IntegerField(primary_key=True, db_column='typeID') # Field name made lowercase.
    activityid = models.IntegerField(primary_key=True, db_column='activityID') # Field name made lowercase.
    requiredtypeid = models.IntegerField(primary_key=True, db_column='requiredTypeID') # Field name made lowercase.
    quantity = models.IntegerField(null=True, blank=True)
    damageperjob = models.FloatField(null=True, db_column='damagePerJob', blank=True) # Field name made lowercase.
    recycle = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ramTypeRequirements'

class Staoperationservices(models.Model):
    operationid = models.IntegerField(primary_key=True, db_column='operationID') # Field name made lowercase.
    serviceid = models.IntegerField(primary_key=True, db_column='serviceID') # Field name made lowercase.
    class Meta:
        db_table = 'staOperationServices'

class Staoperations(models.Model):
    activityid = models.IntegerField(null=True, db_column='activityID', blank=True) # Field name made lowercase.
    operationid = models.IntegerField(primary_key=True, db_column='operationID') # Field name made lowercase.
    operationname = models.CharField(max_length=300, db_column='operationName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    fringe = models.IntegerField(null=True, blank=True)
    corridor = models.IntegerField(null=True, blank=True)
    hub = models.IntegerField(null=True, blank=True)
    border = models.IntegerField(null=True, blank=True)
    ratio = models.IntegerField(null=True, blank=True)
    caldaristationtypeid = models.IntegerField(null=True, db_column='caldariStationTypeID', blank=True) # Field name made lowercase.
    minmatarstationtypeid = models.IntegerField(null=True, db_column='minmatarStationTypeID', blank=True) # Field name made lowercase.
    amarrstationtypeid = models.IntegerField(null=True, db_column='amarrStationTypeID', blank=True) # Field name made lowercase.
    gallentestationtypeid = models.IntegerField(null=True, db_column='gallenteStationTypeID', blank=True) # Field name made lowercase.
    jovestationtypeid = models.IntegerField(null=True, db_column='joveStationTypeID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'staOperations'

class Staservices(models.Model):
    serviceid = models.IntegerField(primary_key=True, db_column='serviceID') # Field name made lowercase.
    servicename = models.CharField(max_length=300, db_column='serviceName', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=3000, blank=True)
    class Meta:
        db_table = 'staServices'

class Stastationtypes(models.Model):
    stationtypeid = models.IntegerField(primary_key=True, db_column='stationTypeID') # Field name made lowercase.
    dockentryx = models.FloatField(null=True, db_column='dockEntryX', blank=True) # Field name made lowercase.
    dockentryy = models.FloatField(null=True, db_column='dockEntryY', blank=True) # Field name made lowercase.
    dockentryz = models.FloatField(null=True, db_column='dockEntryZ', blank=True) # Field name made lowercase.
    dockorientationx = models.FloatField(null=True, db_column='dockOrientationX', blank=True) # Field name made lowercase.
    dockorientationy = models.FloatField(null=True, db_column='dockOrientationY', blank=True) # Field name made lowercase.
    dockorientationz = models.FloatField(null=True, db_column='dockOrientationZ', blank=True) # Field name made lowercase.
    operationid = models.IntegerField(null=True, db_column='operationID', blank=True) # Field name made lowercase.
    officeslots = models.IntegerField(null=True, db_column='officeSlots', blank=True) # Field name made lowercase.
    reprocessingefficiency = models.FloatField(null=True, db_column='reprocessingEfficiency', blank=True) # Field name made lowercase.
    conquerable = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'staStationTypes'

class Stastations(models.Model):
    stationid = models.IntegerField(primary_key=True, db_column='stationID') # Field name made lowercase.
    security = models.IntegerField(null=True, blank=True)
    dockingcostpervolume = models.FloatField(null=True, db_column='dockingCostPerVolume', blank=True) # Field name made lowercase.
    maxshipvolumedockable = models.FloatField(null=True, db_column='maxShipVolumeDockable', blank=True) # Field name made lowercase.
    officerentalcost = models.IntegerField(null=True, db_column='officeRentalCost', blank=True) # Field name made lowercase.
    operationid = models.IntegerField(null=True, db_column='operationID', blank=True) # Field name made lowercase.
    stationtypeid = models.IntegerField(null=True, db_column='stationTypeID', blank=True) # Field name made lowercase.
    corporationid = models.IntegerField(null=True, db_column='corporationID', blank=True) # Field name made lowercase.
    solarsystemid = models.IntegerField(null=True, db_column='solarSystemID', blank=True) # Field name made lowercase.
    constellationid = models.IntegerField(null=True, db_column='constellationID', blank=True) # Field name made lowercase.
    regionid = models.IntegerField(null=True, db_column='regionID', blank=True) # Field name made lowercase.
    stationname = models.CharField(max_length=300, db_column='stationName', blank=True) # Field name made lowercase.
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    reprocessingefficiency = models.FloatField(null=True, db_column='reprocessingEfficiency', blank=True) # Field name made lowercase.
    reprocessingstationstake = models.FloatField(null=True, db_column='reprocessingStationsTake', blank=True) # Field name made lowercase.
    reprocessinghangarflag = models.IntegerField(null=True, db_column='reprocessingHangarFlag', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'staStations'

class Translationtables(models.Model):
    sourcetable = models.CharField(max_length=600, primary_key=True, db_column='sourceTable') # Field name made lowercase.
    destinationtable = models.CharField(max_length=600, db_column='destinationTable', blank=True) # Field name made lowercase.
    translatedkey = models.CharField(max_length=600, primary_key=True, db_column='translatedKey') # Field name made lowercase.
    tcgroupid = models.IntegerField(null=True, db_column='tcGroupID', blank=True) # Field name made lowercase.
    tcid = models.IntegerField(null=True, db_column='tcID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'translationTables'

class Trntranslationcolumns(models.Model):
    tcgroupid = models.IntegerField(null=True, db_column='tcGroupID', blank=True) # Field name made lowercase.
    tcid = models.IntegerField(primary_key=True, db_column='tcID') # Field name made lowercase.
    tablename = models.CharField(max_length=768, db_column='tableName') # Field name made lowercase.
    columnname = models.CharField(max_length=384, db_column='columnName') # Field name made lowercase.
    masterid = models.CharField(max_length=384, db_column='masterID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'trnTranslationColumns'

class Trntranslationlanguages(models.Model):
    numericlanguageid = models.IntegerField(primary_key=True, db_column='numericLanguageID') # Field name made lowercase.
    languageid = models.CharField(max_length=150, db_column='languageID', blank=True) # Field name made lowercase.
    languagename = models.CharField(max_length=600, db_column='languageName', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'trnTranslationLanguages'

class Trntranslations(models.Model):
    tcid = models.IntegerField(primary_key=True, db_column='tcID') # Field name made lowercase.
    keyid = models.IntegerField(primary_key=True, db_column='keyID') # Field name made lowercase.
    languageid = models.CharField(max_length=150, primary_key=True, db_column='languageID') # Field name made lowercase.
    text = models.TextField(blank=True)
    class Meta:
        db_table = 'trnTranslations'

class Warcombatzonesystems(models.Model):
    solarsystemid = models.IntegerField(primary_key=True, db_column='solarSystemID') # Field name made lowercase.
    combatzoneid = models.IntegerField(null=True, db_column='combatZoneID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'warCombatZoneSystems'

class Warcombatzones(models.Model):
    combatzoneid = models.IntegerField(primary_key=True, db_column='combatZoneID') # Field name made lowercase.
    combatzonename = models.CharField(max_length=300, db_column='combatZoneName', blank=True) # Field name made lowercase.
    factionid = models.IntegerField(null=True, db_column='factionID', blank=True) # Field name made lowercase.
    centersystemid = models.IntegerField(null=True, db_column='centerSystemID', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=1500, blank=True)
    class Meta:
        db_table = 'warCombatZones'
