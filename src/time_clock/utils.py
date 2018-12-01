def current_page_round(page_obj):
    '''
    1.当前页面的附近页
    2.保存当前页面的前后两页，以及第一页和最后一页，中间页码用省略号填充
    3.例如当前页为5,总页数为10
    则current_page_round=[1,...,3,4,5,6,7...,10]
    '''
    if page_obj is None:
        return None
    current_page = page_obj.number # 当前页面
    total_page = page_obj.paginator.num_pages # 总页数 
    # print('{} of {}'.format(current_page,total_page)) 
    # 例如current_page=4,total_page=7
    # current_page_round = [2,3,4,5,6]
    current_page_round = list(range(max(current_page-2,1),current_page))+\
    list(range(current_page,min(current_page+2,total_page)+1)) 
    
    # 添加省略号
    if current_page_round[0]-1 >= 2:
        current_page_round.insert(0,'...')
    if current_page_round[-1]-total_page <= -2:
        current_page_round.append('...')
    # 添加首页尾页
    if current_page_round[0] != 1 :
        current_page_round.insert(0,1) # 在0位置插入1
    if current_page_round[-1] != total_page :
        current_page_round.append(total_page)
    # print(current_page_round)
    return current_page_round