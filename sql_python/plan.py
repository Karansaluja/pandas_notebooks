import psycopg2

#check data connection
def function_with_sql():
    con = psycopg2.connect(database = 'joyce_planning_2020', user = 'ivan', password = 'ivan1')
    cur = con.cursor()
    cur.execute("select * from company_abc")

    for record in cur:
        print(record)
    
    con.close()

#start planning function
def start_planning(year, quarter, user, pwd):
    #connect to database
    con = psycopg2.connect(database = "joyce_planning_2020", user = user, password = pwd, host = "localhost")
    cur = con.cursor()


    #step1: Delete plan data from the data_table related to target year and quarter
    cur.execute("delete from plan_data where quarterid=cast(%s.%s as varchar(6))", (year, quarter,))
    con.commit()
    #step2: Delete plan_status related to the target quarter
    cur.execute("delete from plan_status where quarterid=cast(%s.%s as varchar(6))", (year,quarter,))
    con.commit()
    #step3: create planning_status records for the selected quarter
    cur.execute("""insert into plan_status (quarterid, country, status) 
                select distinct %s||'.'||%s quarterid, c2.countryregioncode country, 'R' from country2 c2
                left join (select cs.qr, c.countrycode
                from company_sales cs join company c on c.id=cs.cid where quarter_yr=%s)t
                on t.countrycode = c2.countryregioncode""", (year,quarter,quarter,))
    
    con.commit()
    # step4: generate version n of planning data
    cur.execute("""insert into plan_data
                select 'N' versionid, countryregioncode as country, %s||'.'||%s, productcategoryid as pcid , coalesce(salesamt ,0) as salesamt 
                from country2 cross join productcategory p left join 
                (select c.countrycode country, categoryid pcid, sum(salesamt)/2 as salesamt 
                from company_sales cs left join company as c on cs.cid = c.id where quarter_yr = %s and ccls != 'C'
                group by c.countrycode , categoryid
                order by c.countrycode , categoryid) as t on t.country = countryregioncode and t.pcid = productcategoryid
                order by countryregioncode, productcategoryid""", (year, quarter, quarter))
    con.commit()
    # #step5: copy version n 
    cur.execute("""insert into plan_data(versionid, country, quarterid, pcid, salesamt) 
                   select 'P' versionid, p.country, p.quarterid, p.pcid, p.salesamt from plan_data p""")
    con.commit()
    
    con.close()


# start_planning(2014, 1, 'ivan', 'ivan1')

#set_lock
def set_lock(year, quarter, user, pwd):
    #connect to database
    con = psycopg2.connect(database = "joyce_planning_2020", user = user, password = pwd, host = "localhost")
    cur = con.cursor()

    #change status from R to L
    cur.execute("""update plan_status 
                   set status = 'L',
	               author = %s,
	               modifieddatetime = current_timestamp
                   from country_managers
                   where quarterid = %s||'.'||%s
                   and country_managers.username = %s
                   and country_managers.country = plan_status.country""",(user, year, quarter,user,))
    con.commit()
    con.close()

# set_lock(2014, 1, 'kirill', 'kirill1')
# set_lock(2014, 1, 'sophie', 'sophie1')

#remove_lock
def remove_lock(year, quarter, user, pwd):
    #connect to database
    con = psycopg2.connect(database = "joyce_planning_2020", user = user, password = pwd, host = "localhost")
    cur = con.cursor()

    #change status from L to R
    cur.execute("""update plan_status 
                   set status = 'R',
	               author = %s,
	               modifieddatetime = current_timestamp
                   from country_managers
                   where quarterid = %s||'.'||%s
                   and country_managers.username = %s
                   and country_managers.country = plan_status.country""",(user, year, quarter,user,))
    con.commit()
    con.close()

# remove_lock(2014, 1, 'kirill', 'kirill1')
# remove_lock(2014, 1, 'sophie', 'sophie1')

def accept_plan(year, quarter, user, pwd):
    #connect to database
    con = psycopg2.connect(database = "joyce_planning_2020", user = user, password = pwd, host = "localhost")
    cur = con.cursor()

    #step1: clear A version of plan data for specific quarter and countries accessible to the current user
    cur.execute("""delete from plan_data p
                    using country_managers cm where p.country = cm.country and 
                    cm.username = %s and p.versionid = 'A' and p.quarterid = %s||'.'||%s""", (user,year, quarter,))
    con.commit()

    #step2: read data available to the current user from the version P and save its copy as the version A
    cur.execute("""insert into plan_data (versionid, country, quarterid, pcid, salesamt)
                    select 'A', pd.country, pd.quarterid, pd.pcid, pd.salesamt from plan_data pd
                    join country_managers cm using(country)
                    where cm.username = %s and pd.versionid = 'P' and pd.quarterid = %s||'.'||%s """,(user,year, quarter,))
    con.commit()

    #step 3: change data status from R to A
    cur.execute("""update plan_status 
                   set status = 'A',
	               author = %s,
	               modifieddatetime = current_timestamp
                   from country_managers
                   where quarterid = %s||'.'||%s
                   and country_managers.username = %s
                   and country_managers.country = plan_status.country""",(user, year, quarter,user,))
    con.commit()
    con.close()

accept_plan(2014, 1, 'kirill', 'kirill1')
accept_plan(2014, 1, 'sophie', 'sophie1')